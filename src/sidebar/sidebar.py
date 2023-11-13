import streamlit as st

from .lakera_api_manager import LakeraAPIManager
from .language_manager import LanguageManager
from .model_api_manager import ModelAPIManager


class Sidebar:
    def __init__(self):
        self.language_manager = LanguageManager()
        self.model_api_manager = ModelAPIManager()
        self.lakera_api_manager = LakeraAPIManager()

    def show(self):
        with st.sidebar:
            self.language_manager.main()
            self.model_api_manager.main()
            self.lakera_api_manager.main()
