import streamlit as st

from utils.logging import configure_logger

logger = configure_logger(__file__)


class LanguageManager:
    def __init__(self):
        self.languages = [
            "English",
            "Spanish",
            "French",
            "German",
        ]
        self.selected_language = "English"

    def display(self):
        st.title("Language")

        self.selected_language = st.selectbox(
            label="Select chat language:",
            options=list(self.languages),
            index=list(self.languages).index(self.selected_language),
            on_change=logger.info,
            args=("Switching languages",),
        )

        st.session_state.language = self.selected_language
