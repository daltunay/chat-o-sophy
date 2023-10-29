import streamlit as st
import openai
from dotenv import load_dotenv
import os
import logging

# Load environment variables from .env file
load_dotenv(".env")


class APIKeyManager:
    def __init__(self):
        logging.info("Initializing API key manager")
        self.local_api_key = st.session_state.get(
            "local_api_key", os.getenv("LOCAL_OPENAI_API_KEY")
        )
        self.use_local_key = st.session_state.get("use_local_key", False)
        self.user_api_key = st.session_state.get("user_api_key", "")

    def display_api_form(self):
        with st.sidebar:
            st.title("API Manager")

            self.use_local_key = st.checkbox(
                "Use local API key",
                on_change=self.check_api_key,
                value=st.session_state.get("use_local_key", False),
                key="use_local_key",
                kwargs={"type": "local"},
            )

            with st.form("api_form"):
                self.user_api_key = st.text_input(
                    label="Enter OpenAI API key:",
                    value=self.user_api_key,
                    placeholder="sk-...",
                    type="password",
                    autocomplete="",
                    disabled=self.use_local_key,
                )
                st.form_submit_button(
                    label="Submit",
                    use_container_width=True,
                    disabled=self.use_local_key,
                    on_click=self.check_api_key,
                    kwargs={"type": "user"},
                )

        if st.session_state.get("valid_api_key"):
            st.sidebar.success("Successfully authenticated", icon="🔐")
        else:
            st.sidebar.error("Please add your OpenAI API key to continue")
            st.sidebar.info(
                "Obtain your key from: https://platform.openai.com/account/api-keys"
            )

    def check_api_key(self, type: str):
        api_key = None

        if type == "local" and st.session_state.get("use_local_key"):
            api_key = self.local_api_key
        elif type == "user":
            api_key = self.user_api_key

        try:
            openai.api_key = api_key
            _ = openai.Model.list()
            st.toast("Authentication successful!", icon="✅")
            st.session_state.valid_api_key = True
            self.store_api_key(api_key)
        except openai.error.AuthenticationError:
            st.toast("Authentication error", icon="🚫")
            st.session_state.valid_api_key = False
            self.delete_api_key()

    def store_api_key(self, api_key):
        st.session_state.OPENAI_API_KEY = api_key
        os.environ["OPENAI_API_KEY"] = api_key

    def delete_api_key(self):
        st.session_state.OPENAI_API_KEY = None
        os.environ.pop("OPENAI_API_KEY", None)
