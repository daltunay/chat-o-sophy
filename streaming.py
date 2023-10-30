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


class StreamingCallbacks:
    def __init__(self) -> None:
        self.chat_callback = StreamingChatCallbackHandler()
        self.stdout_callback = StreamingStdOutCallbackHandler()

    @property
    def callbacks(self):
        return [self.chat_callback, self.stdout_callback]
