# decorator
import logging

import streamlit as st

PHILOSOPHER_OPTIONS = ["Nietzsche", "Plato", "Schopenhauer"]


def reset(func):
    st.session_state.setdefault("current_page", func.__qualname__)
    if func.__qualname__ != st.session_state.current_page:
        logging.info("Resetting chat history")
        try:
            st.cache_resource.clear()
            del st.session_state.current_page
            st.session_state.history = []
        except Exception as e:
            logging.error(e)

    def execute(*args, **kwargs):
        func(*args, **kwargs)

    return execute


# decorator
def display_history(func):
    for msg in st.session_state.get("history", {}).get(
        st.session_state.get("current_philosopher"), []
    ):
        display_msg(msg["content"], msg["role"])

    def execute(*args, **kwargs):
        func(*args, **kwargs)

    return execute


def display_msg(msg, author, save=False, write=True):
    """Method to display message on the UI

    Args:
        msg (str): message to display
        author (str): author of the message -user/assistant
    """
    if save:
        st.session_state.history[st.session_state.current_philosopher].append(
            {"role": author, "content": msg}
        )
    if write:
        st.chat_message(author).write(msg)


def enable_user_input(state):
    st.session_state.input_enabled = state
