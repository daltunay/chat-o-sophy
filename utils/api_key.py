import logging
import os

import openai
import streamlit as st
from dotenv import load_dotenv

load_dotenv()


def configure_openai_api_key(home=False):
    logging.info("Configuring OpenAI API key")
    st.sidebar.checkbox(
        label="Community Version (Local API)",
        key="community_version",
    )

    st.sidebar.text_input(
        label="OpenAI API Key",
        type="password",
        placeholder="sk-...",
        autocomplete="",
        key="OPENAI_API_KEY",
        disabled=st.session_state.get("community_version", False),
        on_change=check_openai_api_key,
    )

    if st.session_state.get("community_version"):
        os.environ["OPENAI_API_KEY"] = os.getenv("LOCAL_OPENAI_API_KEY")
    elif st.session_state.get("valid_openai_api_key"):
        os.environ["OPENAI_API_KEY"] = st.session_state.OPENAI_API_KEY
    elif not home:
        st.error("Please add your OpenAI API key to continue.")
        st.info("Obtain your key from: https://platform.openai.com/account/api-keys")
        st.stop()


def check_openai_api_key():
    openai.api_key = st.session_state.get("OPENAI_API_KEY")
    try:
        openai.Model.list()
    except openai.error.AuthenticationError as e:
        st.session_state.valid_openai_api_key = False
    else:
        st.session_state.valid_openai_api_key = True
