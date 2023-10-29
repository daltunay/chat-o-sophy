import logging

import streamlit as st

from chatbots import SingleChatbot
from utils.chat_history import display_history


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

st.set_page_config(page_title="chat-o-sophy", page_icon="💬")

PHILOSOPHERS = ["Nietzsche", "Plato", "Schopenhauer"]


def initialize_chat():
    philosopher_name = st.session_state.current_philosopher
    if (
        philosopher_bot := st.session_state.get("chatbots", {}).get(philosopher_name)
        is None
    ):
        logging.info(f"Initializing chat session with {philosopher_name}")
        philosopher_bot = SingleChatbot(philosopher_name)
        st.session_state.current_philosopher = philosopher_name
        st.session_state.chatbot = philosopher_bot
        st.session_state.chatbots[philosopher_name] = philosopher_bot
    else:
        logging.info(f"Restoring chat session with {philosopher_name}")
        st.session_state.current_philosopher = philosopher_name
        st.session_state.chatbot = st.session_state.chatbots[philosopher_name]


@display_history
def main():
    if not st.session_state.get("api_key_manager"):
        return
    st.session_state.api_key_manager.display_api_form()

    st.session_state.setdefault("header_placeholder", st.empty())
    st.session_state.setdefault("chatbots", {name: None for name in PHILOSOPHERS})
    st.session_state.setdefault("history", {name: [] for name in PHILOSOPHERS})

    with st.session_state.header_placeholder.container():
        st.title("Single mode", anchor=False)
        st.caption("Chat with the philosopher of your choice!")

        st.selectbox(
            label="Philosopher:",
            placeholder="Choose one philosopher",
            key="current_philosopher",
            options=PHILOSOPHERS,
            index=None,
            on_change=initialize_chat,
            disabled=st.session_state.get("OPENAI_API_KEY") is None,
        )

    if current_philosopher := st.session_state.get("current_philosopher"):
        if user_query := st.chat_input(
            placeholder="What do you want to know?",
            disabled=st.session_state.get("chatbot") is None
            or st.session_state.get("OPENAI_API_KEY") is None,
        ):
            st.session_state.chatbot.chat(prompt=user_query)

        if not st.session_state.history[current_philosopher]:
            st.session_state.chatbot.greet()


if __name__ == "__main__":
    main()
