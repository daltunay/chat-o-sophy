import os

import openai
import streamlit as st

from utils.logging import configure_logger

logger = configure_logger(__file__)


class APIManager:
    def __init__(self):
        self.local_api_key = st.session_state.get(
            "local_api_key", st.secrets.openai_api.key
        )
        self.use_local_key = st.session_state.get("use_local_key", False)
        self.user_api_key = st.session_state.get("user_api_key", "")

    def display(self):
        st.title("OpenAI API")

        self.use_local_key = st.checkbox(
            label="Default API key",
            help="Use my own API key, if you don't have any.",
            on_change=self.check_api_key,
            value=st.session_state.get("use_local_key", False),
            key="use_local_key",
            kwargs={"type": "local"},
        )

        with st.form("api_form"):
            self.user_api_key = st.text_input(
                label="Enter your API key:",
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
                kwargs={"type": "human"},
            )

        if st.session_state.get("valid_api_key"):
            st.sidebar.success("Successfully authenticated", icon="🔐")
        else:
            st.sidebar.error("Please add your OpenAI API key to continue")
            st.sidebar.info(
                "Obtain your key from: https://platform.openai.com/account/api-keys"
            )

    def check_api_key(self, type: str):
        logger.info("Checking API key validity")

        api_key = None

        if type == "local" and st.session_state.get("use_local_key"):
            api_key = self.local_api_key
        elif type == "human":
            api_key = self.user_api_key

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
