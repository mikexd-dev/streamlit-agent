import os
import asyncio
import openai
import time
from dotenv import load_dotenv
import streamlit as st
from langchain import SQLDatabase
from langchain.agents import Tool, initialize_agent, AgentType
from langchain.callbacks import StreamlitCallbackHandler
from langchain.chains import LLMMathChain, SQLDatabaseChain, APIChain
from langchain.llms import OpenAI
from langchain.utilities import DuckDuckGoSearchAPIWrapper

from langchain.memory import ConversationBufferMemory
from langchain.agents import (
    Tool,
    AgentExecutor,
)
from langchain import OpenAI, LLMChain
from langchain.tools import Tool
from langchain.agents import ZeroShotAgent, Tool, AgentExecutor
from langchain import PromptTemplate


from langchain.agents import ZeroShotAgent, Tool, AgentExecutor
from langchain.memory import ConversationBufferMemory, ReadOnlySharedMemory
from langchain import OpenAI, LLMChain, PromptTemplate
from datetime import datetime, timedelta, timezone
from openai_functions import shopify_function_calling, nft_function_calling

from langchain.chains.openai_functions import (
    create_openai_fn_chain,
)
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate
from langchain.schema import HumanMessage, SystemMessage


load_dotenv()
dev_db_pw = os.getenv("DEV_DB_PW")
stage_db_pw = os.getenv("STAGE_DB_PW")
prod_db_pw = os.getenv("PROD_DB_PW")

prod_db_uri = os.getenv("PROD_DB_URI")
stage_db_uri = os.getenv("STAGE_DB_URI")
dev_db_uri = os.getenv("DEV_DB_URI")

SHOPIFY_ACCESS_KEY = os.getenv("SHOPIFY_ACCESS_KEY")


def boot():
    # initialize all state variables with default values
    app_variables = {
        "chats": {},
        "chain": None,
        "chat_history": [],
        "chat_container": None,
        "STATE_UPDATING_EMBEDDINGS": False,
        "documents": None,
    }
    for variable in app_variables:
        if variable not in st.session_state:
            st.session_state[variable] = app_variables[variable]


def get_conversation_chain():
    # Setup LLM
    llm = OpenAI(
        temperature=0,
        streaming=True,
        model_name="gpt-3.5-turbo-16k",
    )

    # Setup Summary prompt
    template = """This is a conversation between a human and a bot:

    {chat_history}

    Write a summary of the conversation for {input}:
    """

    prompt = PromptTemplate(input_variables=["input", "chat_history"], template=template)
    memory = ConversationBufferMemory(memory_key="chat_history")
    readonlymemory = ReadOnlySharedMemory(memory=memory)
    summary_chain = LLMChain(
        llm=llm,
        prompt=prompt,
        verbose=True,
        memory=readonlymemory,  # use the read-only memory to prevent the tool from modifying the memory
    )

    print(prompt.template)

    # Prepare tools
    search = DuckDuckGoSearchAPIWrapper()
    llm_math_chain = LLMMathChain.from_llm(llm)
    db = SQLDatabase.from_uri(
        prod_db_uri,
    )
    db_chain = SQLDatabaseChain.from_llm(llm, db)

    # openai function calling - shopify
    prompt_msgs = [
        SystemMessage(
            content="You are a world class REST API developer who has access to all shopify apis"
        ),
        HumanMessage(
            content="Make calls to the relevant function to fetch data in the following input:"
        ),
        HumanMessagePromptTemplate.from_template("{input}"),
        HumanMessage(content="Tips: Make sure to answer in the correct format"),
    ]
    prompt = ChatPromptTemplate(messages=prompt_msgs)
    llm1 = ChatOpenAI(model="gpt-3.5-turbo-0613", temperature=0)
    # shopify_chain = create_openai_fn_chain(
    #     [get_all_abandoned_checkouts], llm1, prompt, verbose=True, memory=readonlymemory
    # )

    # implicit_docs = """
    # Pitchfork has an API with a sample endpoint at https://pitchfork.com/api/v2/search/?genre=experimental&genre=global&genre=jazz&genre=metal&genre=pop&genre=rap&genre=rock&types=reviews&sort=publishdate%20desc%2Cposition%20asc&size=5&start=0&rating_from=0.0
    # """

    # implicit_chain = APIChain.from_llm_and_api_docs(llm, implicit_docs, verbose=True)

    implicit_docs = """
    Shopify has an API with a sample endpoint for abandoned checkout orders: http://localhost:3000/shopify/checkouts?limit=1

    Shopify has an API with a sample endpoint for a count of checkouts from past 90 days orders: http://localhost:3000/shopify/checkouts?created_at_max=2013-10-12T07%3A05%3A27-02%3A00
    """

    implicit_chain = APIChain.from_llm_and_api_docs(llm, implicit_docs, verbose=True)

    # Setup Tools
    tools = [
        Tool(
            name="search-internet",
            func=search.run,
            description="useful for when you need to answer questions about current events. You should ask targeted questions",
        ),
        Tool(
            name="authentick-database",
            func=db_chain.run,
            description="useful for when you need to answer questions about Authentick. Input should be in the form of a question containing full context. All queries should be read only. No POST, UPDATE, DELETE queries allowed. Trigger this only when authentick is mentioned in the conversation",
        ),
        Tool(
            name="calculator",
            func=llm_math_chain.run,
            description="useful for when you need to answer questions about math",
        ),
        # Tool(
        #     name="Summary",
        #     func=summary_chain.run,
        #     description="useful for when you summarize a conversation. The input to this tool should be a string, representing who will read this summary.",
        # ),
        Tool(
            name="shopify",
            func=shopify_function_calling,
            description="useful for when you need to answer questions about admin functionalities in shopify store such as abandoned_orders. Trigger this only when shopify is mentioned in the conversation.",
        ),
        Tool(
            name="nft-realtime-data",
            func=nft_function_calling,
            description="useful for when you need to answer questions about realtime nft information such as top selling nfts, token transfers history, token prices, ",
        ),
    ]

    # Setup prompt
    prefix = """Have a conversation with a human, answering the following questions as best you can. You have access to the following tools:"""
    suffix = """Most of the queries would be regarding the authentick database. However if the result cannot be found in authentick database, you may use the search tool to look for it online. Do not provide false information if nothing can be found!"

    {chat_history}
    Question: {input}
    {agent_scratchpad}"""

    prompt = ZeroShotAgent.create_prompt(
        tools,
        prefix=prefix,
        suffix=suffix,
        input_variables=["input", "chat_history", "agent_scratchpad"],
    )

    print(prompt.template)

    # initialize conversational memory
    # chat_history = MessagesPlaceholder(variable_name="chat_history")
    # memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

    # Initialize agent
    mrkl_chain = initialize_agent(
        tools,
        llm1,
        agent=AgentType.OPENAI_MULTI_FUNCTIONS,
        verbose=True,
        memory=memory,
    )
    # llm_chain = LLMChain(llm=llm, prompt=prompt, verbose=True)
    # agent = ZeroShotAgent(llm_chain=llm_chain, tools=tools, verbose=True)

    # agent_chain = AgentExecutor.from_agent_and_tools(
    #     agent=agent, tools=tools, verbose=True, memory=memory
    # )

    return mrkl_chain


def ask(input: str, callback_func) -> str:
    try:
        response = st.session_state.chain.run(input, callback_func)
    except Exception as e:
        response = str(e)
        if response.startswith("Could not parse LLM output: `"):
            response = response.removeprefix("Could not parse LLM output: `").removesuffix("`")
            return response
        else:
            raise Exception(str(e))


def render_chat():
    if st.session_state.chat_container is None:
        st.session_state.chat_container = st.empty()

    if st.session_state.chat_container:
        st.session_state.chat_container.empty()

    with st.session_state.chat_container.container():
        if not st.session_state.chats:
            return

        with st.expander("Chat History"):
            st.json(st.session_state.chats)

        for id in st.session_state.chats:
            chat = st.session_state.chats[id]
            user = st.chat_message("user")
            user.write(chat["text"])
            assistant = st.chat_message("assistant")

            with assistant:
                if chat["response"] is None:
                    st.write("Thinking ...")
                else:
                    st.write(chat["response"])
                    with st.expander("source_documents"):
                        if chat["source_documents"] is not None:
                            st.write("Source: ")
                            st.markdown(
                                "<ul>",
                                unsafe_allow_html=True,
                            )
                            for docs in chat["source_documents"]:
                                st.markdown(
                                    "<li><a href='"
                                    + docs.metadata["source"]
                                    + f"' target='blank'>{docs.metadata['source']}</a></li>",
                                    unsafe_allow_html=True,
                                )
                            st.markdown(
                                "</ul>",
                                unsafe_allow_html=True,
                            )
                    # col1, col2, col3, _ = st.columns([0.2, 0.075, 0.075, 0.65])
                    # with col1:
                    #     st.write("Is this helpful?")
                    # with col2:
                    #     st.button(label="👍", key=(str("chat_"+str(time.time())+id) + "true"),
                    #               on_click=store_response, args=(id, True))
                    # with col3:
                    #     st.button(label="👎", key=(str("chat_"+str(time.time())+id) + "false"),
                    #               on_click=store_response, args=(id, False))


async def main():
    boot()
    # set page config
    st.set_page_config(
        page_title="MRKL",
        page_icon="🦜",
        layout="wide",
    )
    st.title("✅ Authentick Copilot V1")
    openai.api_key = st.sidebar.text_input("OpenAI API Key", type="password")
    if not openai.api_key:
        st.info("Please add your OpenAI API key to continue.")
        st.stop()

    user_query = st.chat_input(placeholder="Ask me anything!")

    output_container = st.empty()

    if "messages" not in st.session_state or st.sidebar.button("Clear message history"):
        st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]

    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["content"])

    with st.sidebar.expander("Chat History"):
        st.json(st.session_state.chats)

    if user_query:
        id = "username-" + str(int(time.time()))
        chat_obj = {
            "id": id,
            "text": user_query,
            "response": None,
            "response_feedback": None,
            "source": None,
            "updated_at": None,
        }
        st.session_state.chats[id] = chat_obj

        if not st.session_state.chain:
            st.session_state.chain = get_conversation_chain()

        st.session_state.messages.append({"role": "user", "content": user_query})
        st.chat_message("user").write(user_query)

        with st.chat_message("assistant"):
            st_callback = StreamlitCallbackHandler(st.container())
            try:
                answer = st.session_state.chain.run(user_query, callbacks=[st_callback])
            except Exception as e:
                answer = str(e)
                if answer.startswith("Could not parse LLM output: `"):
                    print(answer)
                    answer = answer.removeprefix("Could not parse LLM output: `").removesuffix("`")
                    print(answer, "2")
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                    st.write(answer)
                else:
                    raise Exception(str(e))
            st.session_state.messages.append({"role": "assistant", "content": answer})
            st.write(answer)

        # try:
        #     answer = st.session_state.chain.run(user_query, callbacks=[st_callback])
        # except Exception as e:
        #     answer = str(e)
        #     if answer.startswith("Could not parse LLM output: `"):
        #         print(answer)
        #         answer = answer.removeprefix(
        #             "Could not parse LLM output: `"
        #         ).removesuffix("`")
        #         print(answer, "2")
        #         return answer
        #     else:
        #         raise Exception(str(e))
        # print(answer)

        st.session_state.chats[id]["response"] = answer
        # st.session_state.chats[id]["source"] = answer["source"]
        st.session_state.chats[id]["updated_at"] = datetime.now(
            tz=timezone(timedelta(hours=0))
        ).isoformat()
        st.session_state.chat_history.append((user_query, answer))
        user_query = None

        print(st.session_state.chain.memory.buffer)


if __name__ == "__main__":
    asyncio.run(main())
