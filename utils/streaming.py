import streamlit as st
from langchain.callbacks.base import BaseCallbackHandler
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler


class StreamingChatCallbackHandler(BaseCallbackHandler):
    def __init__(self):
        self.container = st.empty()
        self.text = ""

    def on_llm_new_token(self, token, *args, **kwargs):
        self.text += token
        self.container.markdown(self.text, unsafe_allow_html=True)

    def on_llm_end(self, *args, **kwargs):
        self.container.empty()


class BusyCallbackHandler(BaseCallbackHandler):  # TODO: implement in pages
    def __init__(self):
        pass

    def on_llm_start(self, *args, **kwargs):
        st.session_state.busy = True

    def on_llm_end(self, *args, **kwargs):
        st.session_state.busy = False


class CallbackHandlers:
    def __init__(self):
        self.chat_callback_handler = StreamingChatCallbackHandler()
        self.stdout_callback_handler = StreamingStdOutCallbackHandler()
        self.busy_callback_handler = BusyCallbackHandler()

    @property
    def callbacks(self):
        return [
            self.chat_callback_handler,
            self.stdout_callback_handler,
            self.busy_callback_handler,
        ]
