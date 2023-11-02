import os

import openai
import streamlit as st

from utils.logging import configure_logger

logger = configure_logger(__file__)


class APIManager:
    def __init__(self):
        st.session_state.setdefault("use_local_api_key", False)
        st.session_state.setdefault("user_api_key", "")

    def display(self):
        st.title("OpenAI API")

        st.checkbox(
            label="Default API key",
            help="Use the provided default API key, if you don't have any.",
            key="use_local_api_key",
            value=st.session_state.use_local_api_key,
            on_change=self.check_api_key,
        )

        with st.form("api_form"):
            st.text_input(
                label="Enter your API key:",
                value=st.session_state.user_api_key,
                placeholder="sk-...",
                type="password",
                autocomplete="",
                key="user_api_key",
                disabled=st.session_state.use_local_api_key,
            )

            st.form_submit_button(
                label="Submit",
                use_container_width=True,
                disabled=st.session_state.use_local_api_key,
                on_click=self.check_api_key,
            )

        if st.session_state.get("valid_api_key"):
            st.sidebar.success("Successfully authenticated", icon="🔐")
        else:
            st.sidebar.error("Add your OpenAI API key to continue", icon="🔑")
            st.sidebar.info(
                "Obtain your key from:\n"
                "https://platform.openai.com/account/api-keys",
                icon="💡",
            )

    def check_api_key(self):
        logger.info("Checking API key validity")

        api_key = (
            st.secrets.openai_api.key
            if st.session_state.use_local_api_key
            else st.session_state.user_api_key
        )

        try:
            openai.api_key = api_key
            _ = openai.Model.list()
            st.toast("Authentication successful!", icon="✅")
            logger.info("Authentication to OpenAI API successful")
            st.session_state.valid_api_key = True
            self.store_api_key(api_key)
        except openai.error.AuthenticationError:
            st.toast("Authentication error", icon="🚫")
            logger.info("Authentication to OpenAI API failed")
            st.session_state.valid_api_key = False
            self.delete_api_key()

    def store_api_key(self, api_key):
        logger.info("Storing API key in environment")
        os.environ["OPENAI_API_KEY"] = api_key

    def delete_api_key(self):
        logger.info("Deleting API key")
        os.environ.pop("OPENAI_API_KEY", None)
