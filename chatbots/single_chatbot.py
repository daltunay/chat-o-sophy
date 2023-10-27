import logging

import streamlit as st
from langchain.chains import LLMChain
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
    def __init__(self, philosopher):
        logging.info(f"Initializing chatbot: {philosopher}")
        self.philosopher = philosopher

    @property
    @st.cache_resource
    def template(_self):
        return ChatPromptTemplate.from_messages(
            [
                SystemMessagePromptTemplate.from_template(
                    "You are {philosopher}, the philosopher."
                ),
                MessagesPlaceholder(variable_name="history"),
                HumanMessagePromptTemplate.from_template("{input}"),
            ]
        )

    @property
    @st.cache_resource
    def memory(_self):
        logging.info("Initializing memory")
        return ConversationBufferMemory(
            memory_key="history",
            input_key="input",
            return_messages=True,
            human_prefix="User",
            ai_prefix="Philosopher",
        )

    def callbacks(self):
        logging.info("Initializing callbacks")
        return [StreamingStdOutCallbackHandler(), StreamingChatCallbackHandler()]

    @property
    @st.cache_resource
    def llm(_self):
        logging.info("Initializing LLM")
        return ChatOpenAI(model_name="gpt-3.5-turbo", streaming=True)

    @property
    @st.cache_resource
    def chain(_self):
        logging.info("Initializing chain")
        return LLMChain(
            llm=_self.llm, memory=_self.memory, prompt=_self.template, verbose=True
        )

    @st.cache_resource(show_spinner=False)
    def greet(_self):
        _self.chat(prompt="Greet the user.", is_greetings=True)

    def chat(self, prompt, is_greetings=False):
        if not is_greetings:
            display_msg(msg=prompt, author="user", save=True, write=True)
        with st.chat_message("assistant"):
            bot_response = self.chain.run(
                input=prompt, philosopher=self.philosopher, callbacks=self.callbacks()
            )
            display_msg(msg=bot_response, author="assistant", save=True, write=False)
