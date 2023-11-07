import streamlit as st

from utils.logging import configure_logger

logger = configure_logger(__file__)

LANGUAGES = [
    "English",
    "French",
    "German",
    "Spanish",
]


class LanguageManager:
    def __init__(self, default_language="English"):
        self.languages = LANGUAGES
        self.selected_language = default_language

    def choose_language(self):
        self.selected_language = st.selectbox(
            label="Select chat language:",
            options=list(self.languages),
            key="language_manager.selected_language",
            index=list(self.languages).index(
                st.session_state.get(
                    "language_manager.selected_language", self.selected_language
                )
            ),
            help="Non English languages may only work with `gpt-3.5-turbo`",
            on_change=logger.info,
            kwargs={"msg": "Switching languages"},
        )

    def main(self):
        st.title("Chat Language")
        self.choose_language()
