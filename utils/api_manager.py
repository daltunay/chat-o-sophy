import os
import openai
import baseten
import streamlit as st

from utils.logging import configure_logger

logger = configure_logger(__file__)


class APIManager:
    def __init__(self):
        self.initialize_session_state()

    def initialize_session_state(self):
        st.session_state.setdefault("use_local_api_key", False)
        st.session_state.setdefault("user_api_key_baseten", "")
        st.session_state.setdefault("user_api_key_openai", "")
        st.session_state.setdefault("model_choice", "llama-2-7b-chat")
        st.session_state.setdefault("valid_api_key", False)

    def model_choice_selection(self):
        st.selectbox(
            label="Select the model:",
            options=("llama-2-7b-chat", "gpt3.5-turbo"),
            index=("llama-2-7b-chat", "gpt3.5-turbo").index(
                st.session_state.model_choice
            ),
            key="model_choice",
            on_change=self.check_openai_api_key,
        )

    def default_api_selection(self):
        st.checkbox(
            label="Default API key",
            help="Use the provided default API key, if you don't have any.",
            key="use_local_api_key",
            value=st.session_state.use_local_api_key,
            on_change=self.check_openai_api_key,
        )

    def show_authentification_status(self):
        if st.session_state.valid_api_key:
            st.sidebar.success("Successfully authenticated", icon="🔐")
        else:
            st.sidebar.info("Add your API key to continue", icon="🔑")

    def display(self):
        st.title("LLM API")

        self.model_choice_selection()
        self.default_api_selection()

        if st.session_state.model_choice == "llama-2-7b-chat":
            self.display_baseten_api_key()
        else:
            self.display_openai_api_key()

        self.show_authentification_status()

    def display_baseten_api_key(self):
        with st.form("baseten_api"):
            st.text_input(
                label="Enter your BaseTen API key:",
                value=st.session_state.user_api_key_baseten,
                placeholder="...",
                type="password",
                autocomplete="",
                key="user_api_key_baseten",
                disabled=st.session_state.use_local_api_key,
            )

            st.form_submit_button(
                label="Submit",
                use_container_width=True,
                disabled=st.session_state.use_local_api_key,
                on_click=self.check_baseten_api_key,
            )

    def display_openai_api_key(self):
        with st.form("openai_api"):
            st.text_input(
                label="Enter your OpenAI API key:",
                value=st.session_state.user_api_key_openai,
                placeholder="sk-...",
                type="password",
                autocomplete="",
                key="user_api_key_openai",
                disabled=st.session_state.use_local_api_key,
            )

            st.form_submit_button(
                label="Submit",
                use_container_width=True,
                disabled=st.session_state.use_local_api_key,
                on_click=self.check_openai_api_key,
            )

    def check_baseten_api_key(self):
        logger.info("Checking Baseten API key validity")

        api_key = (
            st.secrets.baseten_api.key
            if st.session_state.use_local_api_key
            else st.session_state.user_api_key_baseten
        )

        try:
            _ = baseten.login(api_key)
            st.toast("Authentication successful!", icon="✅")
            logger.info("Authentication to Baseten API successful")
            st.session_state.valid_api_key = True
            self.store_baseten_api_key(api_key)
        except Exception:
            st.toast("Authentication error", icon="🚫")
            logger.info("Authentication to Baseten API failed")
            st.session_state.valid_api_key = False
            self.delete_baseten_api_key()

    def check_openai_api_key(self):
        logger.info("Checking OpenAI API key validity")

        api_key = (
            st.secrets.openai_api.key
            if st.session_state.use_local_api_key
            else st.session_state.user_api_key_openai
        )

        try:
            openai.api_key = api_key
            _ = openai.Model.list()
            st.toast("Authentication successful!", icon="✅")
            logger.info("Authentication to OpenAI API successful")
            st.session_state.valid_api_key = True
            self.store_openai_api_key(api_key)
        except openai.error.AuthenticationError:
            st.toast("Authentication error", icon="🚫")
            logger.info("Authentication to OpenAI API failed")
            st.session_state.valid_api_key = False
            self.delete_openai_api_key()

    def store_openai_api_key(self, api_key):
        logger.info("Storing OpenAI API key in environment")
        os.environ["OPENAI_API_KEY"] = api_key

    def delete_openai_api_key(self):
        logger.info("Deleting OpenAI API key")
        os.environ.pop("OPENAI_API_KEY", None)

    def store_baseten_api_key(self, api_key):
        logger.info("Storing OpenAI API key in environment")
        os.environ["BASETEN_API_KEY"] = api_key

    def delete_baseten_api_key(self):
        logger.info("Deleting OpenAI API key")
        os.environ.pop("BASETEN_API_KEY", None)
