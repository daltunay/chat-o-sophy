# decorator
import logging

import streamlit as st


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
    if "current_philosopher" in st.session_state:
        for msg in st.session_state.history.get(
            st.session_state.current_philosopher, []
        ):
            st.chat_message(msg["role"]).write(msg["content"])

    return func
