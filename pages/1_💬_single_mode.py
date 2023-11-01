import os

import streamlit as st

from chatbot import PhilosopherChatbot
from utils.chat_history import display_chat_history
from utils.logging import configure_logger

logger = configure_logger(__file__)

st.set_page_config(page_title="chat-o-sophy - single mode", page_icon="💭")


PHILOSOPHERS = [
    os.path.splitext(filename)[0].replace("_", " ").title()
    for filename in os.listdir("philosophers")
]


@display_chat_history
def main():
    logger.info("Running single mode")

    if api_key_manager := st.session_state.get("api_key_manager"):
        api_key_manager.display()

    st.session_state.setdefault("header_container", st.empty())
    st.session_state.setdefault(
        "chatbots",
        {philosopher: PhilosopherChatbot(philosopher) for philosopher in PHILOSOPHERS},
    )

    with st.session_state["header_container"].container():
        st.title("Single mode", anchor=False)
        st.caption("Chat with the philosopher of your choice!")

        current_choice = st.selectbox(
            label="Philosopher:",
            placeholder="Choose one philosopher",
            options=PHILOSOPHERS,
            index=None,
            disabled=not os.getenv("OPENAI_API_KEY"),
        )

    if current_choice:
        logger.info(f"Switching to {current_choice}")
        chatbot = st.session_state.chatbots[current_choice]
        st.session_state.current_chatbot = chatbot
        if chatbot.history == []:
            with st.spinner(f"{current_choice} is writing..."):
                with st.chat_message("ai", avatar=chatbot.avatar):
                    chatbot.greet()

    if prompt := st.chat_input(
        placeholder="What do you want to know?",
        disabled=not (current_choice and os.getenv("OPENAI_API_KEY")),
    ):
        st.chat_message("human").write(prompt)
        with st.spinner(f"{current_choice} is writing..."):
            with st.chat_message("ai", avatar=chatbot.avatar):
                chatbot.chat(prompt)


if __name__ == "__main__":
    main()
