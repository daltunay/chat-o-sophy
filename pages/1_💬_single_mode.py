import contextlib
import os

import streamlit as st

from chatbot import PhilosopherChatbot
from utils.logging import configure_logger
from sidebar import show_sidebar

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


@st.cache_resource(max_entries=1)
def initialize_chatbots(model, language):
    logger.info(f"Initializing chatbots with {model=}, language={language}")
    provider = st.session_state.api_manager.provider
    st.session_state.chatbots = {
        philosopher: PhilosopherChatbot(philosopher, provider=provider)
        for philosopher in PHILOSOPHERS
    }


def main():
    logger.info("Running single mode")

    st.title("Single mode", anchor=False)
    st.caption("Chat with the philosopher of your choice!")

    show_sidebar()

    authentificated = st.session_state.api_manager.authentificated
    chosen_model = st.session_state.api_manager.chosen_model
    selected_language = st.session_state.language_manager.selected_language

    initialize_chatbots(model=chosen_model, language=selected_language)

    current_choice = st.selectbox(
        label="Philosopher:",
        placeholder="Choose one philosopher",
        options=PHILOSOPHERS,
        index=None,
        disabled=not authentificated,
    )

    if current_choice:
        chatbot = st.session_state.chatbots[current_choice]
        display_chat_history(chatbot)
        if chatbot.history == []:
            logger.info(f"Switching to {current_choice}")
            logger.info("Generating greetings")
            with st.spinner(f"{current_choice} is writing..."):
                with st.chat_message("ai", avatar=chatbot.avatar):
                    greetings = chatbot.greet(language=selected_language)
                    st.write(greetings)
    elif authentificated:
        st.info("Select a philosopher in the above menu", icon="ℹ️")
    else:
        st.error(
            "Please configure the model API in left sidebar to unlock selection",
            icon="🔒",
        )

    if prompt := st.chat_input(
        placeholder="What do you want to know?",
        disabled=not (current_choice and authentificated),
    ):
        logger.info("User prompt submitted")
        st.chat_message("human").write(prompt)
        with st.spinner(f"{current_choice} is writing..."):
            logger.info("Generating response to user prompt")
            with st.chat_message("ai", avatar=chatbot.avatar):
                st.write(chatbot.chat(prompt, language=selected_language))


if __name__ == "__main__":
    main()
