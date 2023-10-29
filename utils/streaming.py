import streamlit as st
from langchain.callbacks.base import BaseCallbackHandler
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler


class StreamingChatCallbackHandler(BaseCallbackHandler):
    def __init__(self):
        self.container = st.empty()
        self.response = ""

    def on_llm_new_token(self, token: str, **kwargs):
        self.response += token
        self.container.markdown(self.response)
