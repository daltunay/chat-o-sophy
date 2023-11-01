import contextlib
import os

import streamlit as st

from chatbot import PhilosopherChatbot
from utils.api_manager import APIManager
from utils.language_manager import LanguageManager
from utils.logging import configure_logger

logger = configure_logger(__file__)

st.set_page_config(page_title="chat-o-sophy - single mode", page_icon="💭")


PHILOSOPHERS = [
    os.path.splitext(filename)[0].replace("_", " ").title()
    for filename in os.listdir("philosophers")
]


def display_chat_history(chatbot):
    with contextlib.suppress(Exception):
        for message in chatbot.history:
            role, content = message["role"], message["content"]
            avatar = chatbot.avatar if role == "ai" else None
            st.chat_message(role, avatar=avatar).write(content)


def main():
    logger.info("Running single mode")

    st.session_state.setdefault("language_manager", LanguageManager())
    st.session_state.setdefault("api_manager", APIManager())

    with st.sidebar:
        st.session_state.language_manager.display()
        st.divider()
        st.session_state.api_manager.display()

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

    if not os.getenv("OPENAI_API_KEY"):
        st.error("Configure OpenAI API key in left sidebar to unlock selection")

    if current_choice:
        chatbot = st.session_state.chatbots[current_choice]
        display_chat_history(chatbot)
        if chatbot.history == []:
            logger.info(f"Switching to {current_choice}")
            logger.info("Generating greetings")
            with st.spinner(f"{current_choice} is writing..."):
                with st.chat_message("ai", avatar=chatbot.avatar):
                    chatbot.greet(language=st.session_state.language)

    if prompt := st.chat_input(
        placeholder="What do you want to know?",
        disabled=not (current_choice and os.getenv("OPENAI_API_KEY")),
    ):
        logger.info("User prompt submitted")
        st.chat_message("human").write(prompt)
        with st.spinner(f"{current_choice} is writing..."):
            logger.info("Generating response to user prompt")
            with st.chat_message("ai", avatar=chatbot.avatar):
                chatbot.chat(prompt, language=st.session_state.language)


if __name__ == "__main__":
    main()
