import streamlit as st

# initialize all state variables with default values
app_variables = {
    "vs": None,
    "namespace": None,
    "storage_client": None,
    "current_session": None,
    "chats": {},
    "chat_history": [],
    "openai_api_key": "",
}
for variable in app_variables:
    if variable not in st.session_state:
        st.session_state[variable] = app_variables[variable]


# Streamlit app
st.subheader("Settings")

# Get API keys
st.text("Please Enter a valid OpenAI API Key before proceeding further")
openai_api_key = st.text_input(
    "OpenAI API Key", value=st.session_state.openai_api_key, type="password"
)
st.caption("*Required for all apps; get it [here](https://platform.openai.com/account/api-keys).*")

# serper_api_key = st.text_input(
#     "Serper API Key", value=st.session_state.serper_api_key, type="password"
# )
# st.caption("*Required for news and search; get it [here](https://serper.dev/api-key).*")

# If the 'Save' button is clicked
if st.button("Save"):
    if not openai_api_key.strip():
        st.error("Please provide the missing API key.")
    else:
        st.session_state.openai_api_key = openai_api_key
        # st.session_state.serper_api_key = serper_api_key
