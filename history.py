import contextlib

import streamlit as st


# decorator
def display_chat_history(func):
    def execute(*args, **kwargs):
        with contextlib.suppress(Exception):
            current_choice = st.session_state.single_mode["current_choice"]
            current_chatbot = st.session_state.single_mode["chatbots"][current_choice]

            for message in current_chatbot.history:
                role, content = message["role"], message["content"]
                st.chat_message(role).write(content)

        func(*args, **kwargs)

    return execute
