import contextlib
import os

import streamlit as st

from chatbot import PhilosopherChatbot
from utils.logging import configure_logger
from sidebar import Sidebar

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
            if role == "ai":
                st.chat_message(role, avatar=chatbot.avatar).markdown(content)
            else:
                st.chat_message(role).markdown(content)


def initialize_chatbot(model_name, provider, model_owner, model_version):
    st.session_state.chatbot = PhilosopherChatbot(
        philosopher=st.session_state.current_choice,
        provider=provider,
        model_name=model_name,
        model_owner=model_owner,
        model_version=model_version,
    )


def main():
    logger.info("Running single mode")

    st.title("Single mode", anchor=False)
    st.caption("Chat with the philosopher of your choice!")

    sidebar = st.session_state.setdefault("sidebar", Sidebar())
    sidebar.show()

    authentificated = sidebar.api_manager.authentificated
    provider = sidebar.api_manager.provider
    chosen_model = sidebar.api_manager.chosen_model
    model_owner = sidebar.api_manager.model_owner
    model_version = sidebar.api_manager.model_version
    selected_language = sidebar.language_manager.selected_language

    current_choice = st.selectbox(
        label="Philosopher:",
        placeholder="Choose one philosopher",
        options=PHILOSOPHERS,
        index=None,
        key="current_choice",
        disabled=not authentificated,
        on_change=initialize_chatbot,
        kwargs={
            "model_name": chosen_model,
            "provider": provider,
            "model_owner": model_owner,
            "model_version": model_version,
        },
    )

    if chatbot := st.session_state.get("chatbot"):
        display_chat_history(chatbot)

        if chatbot.history == []:
            with st.chat_message("ai", avatar=chatbot.avatar):
                greetings = chatbot.greet(language=selected_language)
                st.markdown(greetings)

        if prompt := st.chat_input(
            placeholder="What do you want to know?",
            disabled=not (current_choice and authentificated),
        ):
            st.chat_message("human").markdown(prompt)
            with st.chat_message("ai", avatar=chatbot.avatar):
                response = chatbot.chat(prompt, language=selected_language)
                st.markdown(response)

    elif authentificated:
        st.info("Select a philosopher in the above menu", icon="ℹ️")
    else:
        st.error("Please configure API in left sidebar to unlock selection", icon="🔒")


if __name__ == "__main__":
    main()
