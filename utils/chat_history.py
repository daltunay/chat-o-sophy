import contextlib

import streamlit as st


def display_chat_history():
    # Function to explicitly display chat history for the current philosopher
    with contextlib.suppress(Exception):
        current_chatbot = st.session_state.current_chatbot
        for message in current_chatbot.history:
            role, content = message["role"], message["content"]
            avatar = current_chatbot.avatar if role == "ai" else None
            st.chat_message(role, avatar=avatar).write(content)