import streamlit as st
from langchain.schema.messages import AIMessage, HumanMessage

st.header("single_mode")
st.write(st.session_state.get("single_mode"))


st.header("multi_mode")
st.write(st.session_state.get("multi_mode"))

st.header("busy")
st.write(st.session_state.get("busy"))