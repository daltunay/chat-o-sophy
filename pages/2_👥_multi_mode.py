import logging

import streamlit as st

from chatbots import MultiChatbots

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

st.set_page_config(page_title="chat-o-sophy", page_icon="💬")

PHILOSOPHERS = ["Nietzsche", "Plato", "Schopenhauer"]


def initialize_chat():
    multi_chatbots = MultiChatbots(philosophers=st.session_state.current_philosophers)
    st.session_state.multi_chatbots = multi_chatbots


def main():
    if api_key_manager := st.session_state.get("api_key_manager"):
        api_key_manager.display_api_form()

    st.session_state.setdefault("header_placeholder", st.empty())
    st.session_state.setdefault("multi_chatbots", None)

    with st.session_state.header_placeholder.container():
        st.title("Multi mode", anchor=False)
        st.caption("Ask a question to several philosophers!")

        st.multiselect(
            label="Philosophers:",
            placeholder="Choose several philosophers",
            key="current_philosophers",
            options=PHILOSOPHERS,
            max_selections=3,
            default=None,
            disabled=st.session_state.get("OPENAI_API_KEY") is None,
            on_change=initialize_chat,
        )

    if user_query := st.chat_input(
        placeholder="What is your question?",
        disabled=st.session_state.get("current_philosophers") == []
        or st.session_state.get("OPENAI_API_KEY") is None,
    ):
        st.session_state.multi_chatbots.ask(user_query)


if __name__ == "__main__":
    main()
