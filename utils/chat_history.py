import streamlit as st
from langchain.schema.messages import HumanMessage, AIMessage


# decorator
def display_history(func):
    try:
        current_choice = st.session_state["single_mode.current_choice"]
        current_chatbot = st.session_state.single_mode[current_choice]
        for message in current_chatbot.memory.chat_memory.messages:
            if isinstance(message, AIMessage):
                st.chat_message("ai").write(message.content)
            if isinstance(message, HumanMessage):
                st.chat_message("human").write(message.content)
    except Exception:
        print("ERROR WHEN DISPLAYING History")

    def execute(*args, **kwargs):
        func(*args, **kwargs)

    return execute
