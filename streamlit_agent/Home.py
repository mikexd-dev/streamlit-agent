from dotenv import load_dotenv
import streamlit as st
import os
from streamlit_supabase_auth import login_form, logout_button
from supabase import StorageException
from storage3 import create_client

from chat_ui import init_ui as chat_ui_init

# from generate_embeddings import load_vs
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

st.set_page_config(page_title="Ticky AI", page_icon=":robot:")
st.title("✅ Authentick Copilot V1")
st.sidebar.title("Authentick Copilot")


def boot():
    # initialize all state variables with default values
    app_variables = {
        "vs": None,
        "namespace": None,
        "storage_client": None,
        "current_session": None,
        "chats": {},
        "chat_history": [],
    }
    for variable in app_variables:
        if variable not in st.session_state:
            st.session_state[variable] = app_variables[variable]


def main():
    boot()

    session = login_form(url=SUPABASE_URL, apiKey=SUPABASE_KEY)

    if not session:
        st.session_state.chats = {}
        st.session_state.chat_history = []
        st.session_state.documents = None
        return

    # Update query param to reset url fragments
    st.experimental_set_query_params(page=["success"])
    with st.sidebar:
        st.write(f"Welcome {session['user']['email']}")
        st.session_state.namespace = session["user"]["email"]
        headers = {
            "apiKey": SUPABASE_KEY,
            "Authorization": f"Bearer {session['access_token']}",
        }
        st.session_state.storage_client = create_client(
            SUPABASE_URL + "/storage/v1", headers, is_async=False
        )
        if logout_button():
            print("hello world")

    if st.session_state.namespace is None:
        return

    # st.session_state.vs = load_vs(st.session_state.namespace)

    # file_uploader_init()
    chat_ui_init()


main()
