import os
from dotenv import load_dotenv

# LLM
from langchain import OpenAI
from langchain.chat_models import ChatOpenAI

# Utils
from langchain.utilities import DuckDuckGoSearchAPIWrapper
from langchain import SerpAPIWrapper

# DB
from langchain import SQLDatabase

# Prompt
# from langchain.prompts import (
#     PromptTemplate,
#     ChatPromptTemplate,
#     HumanMessagePromptTemplate,
# )
# from langchain.schema import HumanMessage, SystemMessage

# Memory
from langchain.memory import ConversationBufferMemory, ReadOnlySharedMemory

# Chains
from langchain.chains import LLMMathChain, SQLDatabaseChain

# Function Calling
from openai_functions import shopify_function_calling, nft_function_calling

# Agent
from langchain.agents import Tool, initialize_agent, AgentType, ZeroShotAgent

load_dotenv()
PROD_DB_URI = os.getenv("PROD_DB_URI")
SIXTEEEN_K_MODEL = "gpt-3.5-turbo-16k"
FUNCTION_CALL_MODEL = "gpt-3.5-turbo-0613"


def get_conversation_chain():
    # Setup LLM
    llm = OpenAI(temperature=0, streaming=True, model_name=SIXTEEEN_K_MODEL)
    llm1 = ChatOpenAI(model=FUNCTION_CALL_MODEL, temperature=0, streaming=True)

    # Setup Memory
    memory = ConversationBufferMemory(memory_key="chat_history")
    readonlymemory = ReadOnlySharedMemory(memory=memory)

    # Prepare tools: SEARCH, MATH, DB
    search = DuckDuckGoSearchAPIWrapper()
    db = SQLDatabase.from_uri(PROD_DB_URI)

    # Setup Chains
    llm_math_chain = LLMMathChain.from_llm(llm, verbose=True, memory=readonlymemory)
    db_chain = SQLDatabaseChain.from_llm(llm, db, verbose=True, memory=readonlymemory)
    search_chain = SerpAPIWrapper(serpapi_api_key=os.getenv("SERPAPI_API_KEY"))

    # Setup Tools
    tools = [
        Tool(
            name="search-internet",
            func=search_chain.run,
            description="useful for when you need to answer questions about current events. You should ask targeted questions. Only use this tool as a last resort when no other tools are helpful",
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

    # Initialize agent
    mrkl_chain = initialize_agent(
        tools,
        llm1,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True,
        memory=memory,
    )

    return mrkl_chain


# IMPLICIT API CHAIN CODE

# shopify_chain = create_openai_fn_chain(
#     [get_all_abandoned_checkouts], llm1, prompt, verbose=True, memory=readonlymemory
# )

# implicit_docs = """
# Pitchfork has an API with a sample endpoint at https://pitchfork.com/api/v2/search/?genre=experimental&genre=global&genre=jazz&genre=metal&genre=pop&genre=rap&genre=rock&types=reviews&sort=publishdate%20desc%2Cposition%20asc&size=5&start=0&rating_from=0.0
# """

# implicit_chain = APIChain.from_llm_and_api_docs(llm, implicit_docs, verbose=True)

# implicit_docs = """
# Shopify has an API with a sample endpoint for abandoned checkout orders: http://localhost:3000/shopify/checkouts?limit=1

# Shopify has an API with a sample endpoint for a count of checkouts from past 90 days orders: http://localhost:3000/shopify/checkouts?created_at_max=2013-10-12T07%3A05%3A27-02%3A00
# """

# implicit_chain = APIChain.from_llm_and_api_docs(llm, implicit_docs, verbose=True)


# SUMMARY CHAIN CODE

# Setup Summary prompt
# template = """This is a conversation between a human and a bot:
# {chat_history}
# Write a summary of the conversation for {input}:
# """

# prompt = PromptTemplate(
#     input_variables=["input", "chat_history"], template=template
# )

# summary_chain = LLMChain(
#     llm=llm,
#     prompt=prompt,
#     verbose=True,
#     memory=readonlymemory,  # use the read-only memory to prevent the tool from modifying the memory
# )
