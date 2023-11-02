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
            on_change=self.check_api_key,
        )

    def api_key_input(self, provider, display_label):
        with st.form(provider + "_api"):
            st.text_input(
                label=f"Enter your {provider.capitalize()} API key:",
                value=st.session_state.get(f"user_api_key_{provider}"),
                placeholder="...",
                type="password",
                autocomplete="",
                key=f"user_api_key_{provider}",
                disabled=st.session_state.use_local_api_key,
            )

            st.form_submit_button(
                label="Submit",
                use_container_width=True,
                disabled=st.session_state.use_local_api_key,
                on_click=lambda: self.check_api_key(provider),
            )

    def check_api_key(self, provider):
        logger.info(f"Checking {provider.capitalize()} API key validity")
        api_key = (
            st.secrets.get(f"{provider}_api").key
            if st.session_state.use_local_api_key
            else st.session_state.get(f"user_api_key_{provider}")
        )

        try:
            if provider == "openai":
                openai.api_key = api_key
                _ = openai.Model.list()
            else:
                _ = baseten.login(api_key)

            st.toast("Authentication successful!", icon="✅")
            logger.info(f"Authentication to {provider.capitalize()} API successful")
            st.session_state.valid_api_key = True
            self.store_api_key(provider, api_key)
        except Exception as e:
            st.toast("Authentication error", icon="🚫")
            logger.info(f"Authentication to {provider.capitalize()} API failed: {e}")
            st.session_state.valid_api_key = False
            self.delete_api_key(provider)

    def store_api_key(self, provider, api_key):
        logger.info(f"Storing {provider.capitalize()} API key in environment")
        os.environ[f"{provider.upper()}_API_KEY"] = api_key

    def delete_api_key(self, provider):
        logger.info(f"Deleting {provider.capitalize()} API key")
        os.environ.pop(f"{provider.upper()}_API_KEY", None)

    def show_authentification_status(self):
        if st.session_state.valid_api_key:
            st.sidebar.success("Successfully authenticated", icon="🔐")
        else:
            st.sidebar.info("Add your API key to continue", icon="🔑")

    def main(self):
        st.title("LLM API")

        self.model_choice_selection()

        if st.session_state.model_choice == "llama-2-7b-chat":
            self.api_key_input("baseten", "BaseTen")
        else:
            self.api_key_input("openai", "OpenAI")

        self.show_authentification_status()
