# decorator
import logging

import streamlit as st


# decorator
def display_history(func):
    def wrapper(*args, **kwargs):
        current_philosopher = st.session_state.get("current_philosopher")
        if current_philosopher:
            history = st.session_state.history.get(current_philosopher, [])
            for message in history:
                st.chat_message(message["role"]).write(message["content"])

        return func(*args, **kwargs)

    return wrapper
