import streamlit as st

from .api_manager import APIManager
from .language_manager import LanguageManager


def show_sidebar():
    st.session_state.setdefault("language_manager", LanguageManager())
    st.session_state.setdefault("api_manager", APIManager())

    with st.sidebar:
        st.session_state.language_manager.main()
        st.session_state.api_manager.main()
