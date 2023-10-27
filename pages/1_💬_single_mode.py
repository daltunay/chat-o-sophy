import logging

import streamlit as st

from chatbots import SingleChatbot
from utils.api_key import configure_openai_api_key
from utils.chat_history import display_history, display_msg

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

PHILOSOPHER_OPTIONS = ["Nietzsche", "Plato", "Schopenhauer"]

st.set_page_config(page_title="chat-o-sophy", page_icon="💬")
st.title("Chatbot")
st.caption("Allows users to interact with the LLM")
st.write(
    "["
    "![source code]"
    "(https://img.shields.io/badge/view_source_code-gray?logo=github)"
    "]"
    "(https://github.com/)"
)
selectbox_placeholder = st.empty()


def initialize_chat():
    if not st.session_state.get("_OPENAI_API_KEY"):
        return

    philosopher = st.session_state.current_philosopher

    logging.info(f"Initializing chat session: {philosopher=}")
    if not st.session_state.get("chatbots", {}).get(philosopher):
        with selectbox_placeholder.container():
            chatbot = SingleChatbot(philosopher)
        st.session_state.chatbots[philosopher] = chatbot
        st.session_state.chatbot = chatbot


@display_history
def main():
    configure_openai_api_key()

    st.session_state.setdefault(
        "chatbots", {philosopher: None for philosopher in PHILOSOPHER_OPTIONS}
    )
    st.session_state.setdefault(
        "history", {philosopher: [] for philosopher in PHILOSOPHER_OPTIONS}
    )

    with selectbox_placeholder.container():
        st.selectbox(
            label="Philosopher:",
            placeholder="Choose one philosopher",
            key="current_philosopher",
            options=PHILOSOPHER_OPTIONS,
            index=None,
            on_change=initialize_chat,
            disabled=st.session_state.get("_OPENAI_API_KEY") is None,
        )

    if user_query := st.chat_input(
        placeholder="Ask me anything!",
        disabled=st.session_state.get("chatbot") is None
        or st.session_state.get("_OPENAI_API_KEY") is None,
    ):
        st.session_state.chatbot.chat(user_query)


if __name__ == "__main__":
    main()
