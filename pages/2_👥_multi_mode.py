import streamlit as st

from chatbots import MultiChatbots
from utils.logging import configure_logger


st.set_page_config(page_title="chat-o-sophy", page_icon="💬")

PHILOSOPHERS = ["Nietzsche", "Plato", "Schopenhauer"]


def initialize_chat():
    philosopher_names = st.session_state.current_philosophers
    logger.info(f"Initializing chat session with {philosopher_names}")
    multi_chatbots = MultiChatbots(philosophers=philosopher_names)
    st.session_state.multi_chatbots = multi_chatbots


def main():
    logger.info("Running multi mode")
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
        )

    if user_query := st.chat_input(
        placeholder="What is your question?",
        disabled=st.session_state.get("current_philosophers") == []
        or st.session_state.get("OPENAI_API_KEY") is None,
    ):
        initialize_chat()
        st.session_state.multi_chatbots.ask(user_query)


if __name__ == "__main__":
    logger = configure_logger(__file__)
    main()
