import streamlit as st
from langchain.schema.messages import HumanMessage, AIMessage

st.header("single_mode")
st.write(st.session_state.get("single_mode"))

st.header("current_choice")
st.write(st.session_state.get("single_mode.current_choice"))


st.header("history")
if single_mode := st.session_state.get("single_mode"):
    if current_choice := st.session_state.get("single_mode.current_choice"):
        chatbot = st.session_state.single_mode[current_choice]["chatbot"]
        memory = chatbot.memory
        for message in memory.chat_memory.messages:
            if isinstance(message, AIMessage):
                message = {"role": "ai", "message": message.content}
                st.write(message)
            if isinstance(message, HumanMessage):
                message = {"role": "human", "message": message.content}
                st.write(message)
