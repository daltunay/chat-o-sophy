import logging

import streamlit as st

from chatbots import SingleChatbot
from utils.api_key import configure_openai_api_key
from utils.chat_history import display_history, enable_user_input, reset

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

st.set_page_config(page_title="chat-o-sophy", page_icon="💬")
st.title("Chatbot")
st.caption("Allows users to interact with the LLM")
st.write(
    "[![source code](https://img.shields.io/badge/view_source_code-gray?logo=github)](https://github.com/)"
)


@reset
@display_history
def main():
    configure_openai_api_key()
    if "chatbot" not in st.session_state:
        st.session_state.chatbot = SingleChatbot()
        st.session_state.history = []

    enable_user_input(
        st.session_state.get("valid_openai_api_key")
        or st.session_state.get("community_version")
    )
    if user_query := st.chat_input(
        placeholder="Ask me anything!",
        disabled=not st.session_state.input_enabled,
        on_submit=enable_user_input,
        kwargs={"state": False},
    ):
        st.session_state.chatbot.chat(user_query)


if __name__ == "__main__":
    main()
