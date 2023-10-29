import streamlit as st

st.header("history")
st.write(st.session_state.get("history"))
