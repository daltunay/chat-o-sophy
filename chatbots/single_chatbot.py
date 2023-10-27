import logging

import streamlit as st
from langchain.chains import ConversationChain
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
    SystemMessagePromptTemplate,
)

from utils.chat_history import display_msg
from utils.streaming import StreamingChatCallbackHandler, StreamingStdOutCallbackHandler


class SingleChatbot:
    def __init__(self):
        logging.info("Initializing chatbot")
        # TODO: import templates

    @property
    @st.cache_resource
    def memory(_self):
        logging.info("Initializing memory")
        return ConversationBufferMemory(ai_prefix="Assistant", human_prefix="User")

    def callbacks(self):
        logging.info("Initializing callbacks")
        return [StreamingStdOutCallbackHandler(), StreamingChatCallbackHandler()]

    @property
    @st.cache_resource
    def llm(_self):
        logging.info("Initializing LLM")
        return ChatOpenAI(
            model_name="gpt-3.5-turbo",
            streaming=True,
        )

    @property
    @st.cache_resource
    def chain(_self):
        logging.info("Initializing chain")
        return ConversationChain(
            llm=_self.llm,
            memory=_self.memory,
            verbose=True,
        )

    @st.cache_resource
    def greet(_self):
        greetings = _self.chain.run("Please greet your user in French.")
        display_msg(msg=greetings, author="assistant", save=True)

    def chat(self, prompt):
        display_msg(msg=prompt, author="user", save=True, write=True)
        with st.chat_message("assistant"):
            bot_response = self.chain.run(prompt, callbacks=self.callbacks())
            display_msg(msg=bot_response, author="assistant", save=True, write=False)
