import contextlib

import streamlit as st


# decorator
def display_chat_history(func):
    def execute(*args, **kwargs):
        with contextlib.suppress(Exception):
            current_chatbot = st.session_state.current_chatbot
            for message in current_chatbot.history:
                role, content = message["role"], message["content"]
                avatar = current_chatbot.avatar if role == "ai" else None
                st.chat_message(role, avatar=avatar).write(content)

        func(*args, **kwargs)

    return execute
