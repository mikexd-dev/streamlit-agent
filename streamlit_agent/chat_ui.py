import asyncio
import openai
import time
import streamlit as st
from annotated_text import annotated_text
from streamlit_extras.switch_page_button import switch_page
from datetime import datetime, timedelta, timezone
from chain_retrieval import get_conversation_chain
from langchain.callbacks import StreamlitCallbackHandler


def boot():
    # initialize all state variables with default values
    app_variables = {
        "chats": {},
        "chain": None,
        "chat_history": [],
        "chat_container": None,
        "STATE_UPDATING_EMBEDDINGS": False,
        "documents": None,
        "openai_api_key": "",
    }
    for variable in app_variables:
        if variable not in st.session_state:
            st.session_state[variable] = app_variables[variable]


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


def init_ui():
    boot()

    header = st.container()
    with header:
        st.subheader("Ticky Q&A")
        annotated_text(
            "Currently support all read operation of ",
            ("Registry Database", "SQLDatabase"),
            ", Query of ",
            ("Realtime NFT Data", "Reservoir API"),
            ", Access ",
            ("Shopify Admin functionalities", "Shopify API"),
            ", and ",
            ("Internet Search", "DuckDuckGoSearchAPIWrapper"),
            ".",
        )
        st.caption(
            "Note: query might have to be more specific in the domain of where to look for the data: e.g. 'get 10 latest nft collections in authentick' vs 'get top nft collections in the last 24 hours'"
        )
    header.write("""<div class='fixed-header'/>""", unsafe_allow_html=True)

    ### Custom CSS for the sticky header
    st.markdown(
        """
    <style>
        div[data-testid="stVerticalBlock"] div:has(div.fixed-header) {
            position: sticky;
            top: 2.875rem;
            background-color: rgb(14, 17, 23);
            z-index: 999;
        }
        .fixed-header {
            border-bottom: 1px solid black;
        }
    </style>
        """,
        unsafe_allow_html=True,
    )

    openai.api_key = st.session_state.openai_api_key
    if not openai.api_key:
        st.info("Please add your OpenAI API key in settings page to continue.")
        switch_page("Settings")
        st.stop()

    user_query = st.chat_input(placeholder="Ask me anything!")

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


# if __name__ == "__main__":
#     main()
