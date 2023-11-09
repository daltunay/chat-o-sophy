import streamlit as st

from .api_manager import APIManager
from .language_manager import LanguageManager


class Sidebar:
    def __init__(self):
        self.language_manager = LanguageManager()
        self.api_manager = APIManager()

    def show(self):
        with st.sidebar:
            self.language_manager.main()
            self.api_manager.main()
