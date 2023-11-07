import streamlit as st

from .api_manager import APIManager
from .language_manager import LanguageManager


class Sidebar:
    def __init__(self):
        self.language_manager = LanguageManager()
        self.api_manager = APIManager()

    def show(self, show_language=True, show_api=True):
        with st.sidebar:
            if show_language:
                self.language_manager.main()
            if show_api:
                self.api_manager.main()
