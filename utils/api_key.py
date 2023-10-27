import logging
import os

import openai
import streamlit as st
from dotenv import load_dotenv

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

load_dotenv()


def configure_openai_api_key():
    st.sidebar.header("OpenAI API")

    # Community version checkbox
    if st.sidebar.checkbox(
        label="Community Version",
        key="community_version",
        value=st.session_state.get(
            "community_version", st.session_state.get("_community_version", False)
        ),
    ):
        os.environ["OPENAI_API_KEY"] = os.getenv("LOCAL_OPENAI_API_KEY")
    st.session_state._community_version = st.session_state.community_version  # memorize

    # API key text input
    st.sidebar.text_input(
        label="OpenAI API Key",
        type="password",
        value=""
        if st.session_state.get("community_version")
        else st.session_state.get("_OPENAI_API_KEY", ""),
        placeholder="sk-...",
        autocomplete="",
        key="OPENAI_API_KEY",
        disabled=st.session_state.get("community_version", False),
        on_change=check_openai_api_key,
    )
    if st.session_state.get("valid_openai_api_key"):
        st.session_state._OPENAI_API_KEY = st.session_state.OPENAI_API_KEY  # memorize
        os.environ["OPENAI_API_KEY"] = st.session_state.OPENAI_API_KEY

    # Toast
    if not (
        st.session_state.get("community_version")
        or st.session_state.get("valid_openai_api_key")
    ):
        st.error("Please add your OpenAI API key to continue.")
        st.info("Obtain your key from: https://platform.openai.com/account/api-keys")
        st.stop()


def check_openai_api_key():
    openai.api_key = st.session_state.get("OPENAI_API_KEY")
    try:
        _ = openai.Model.list()
        logging.info("Authentication successful!")
        st.toast("Authentication successful!", icon="✅")
        st.session_state.valid_openai_api_key = True
    except openai.error.AuthenticationError:
        logging.error("Authentication error")
        st.toast("Authentication error", icon="🚫")
        st.session_state.valid_openai_api_key = False
