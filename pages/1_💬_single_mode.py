import logging

import streamlit as st

from chatbots import SingleChatbot
from utils.api_key import configure_openai_api_key
from utils.chat_history import display_history

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


@display_history
def main():
    configure_openai_api_key()

    if "chatbot" not in st.session_state:
        st.session_state.chatbot = SingleChatbot(philosopher="Nietzsche")
        st.session_state.history = []

    if user_query := st.chat_input(
        placeholder="Ask me anything!",
        disabled=st.session_state.get("chatbot") is None
        or st.session_state.get("OPENAI_API_KEY") is None,
    ):
        st.session_state.chatbot.chat(user_query)


if __name__ == "__main__":
    main()
