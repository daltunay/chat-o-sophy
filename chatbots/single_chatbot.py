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

from utils.streaming import StreamingChatCallbackHandler, StreamingStdOutCallbackHandler

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

INITIAL_PROMPT = "I am your guest. Please present yourself, greet me, and explain me the main topics you are interested in as a philosopher. Keep it very short."


class SingleChatbot:
    def __init__(self, philosopher, role="assistant"):
        logging.info(f"Initializing chatbot: {philosopher}")
        self.philosopher = philosopher
        if role == "assistant":
            self.role = "assistant"
        elif role == "name":
            self.role = philosopher
        self.history = st.session_state.history[philosopher]

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

    def greet(self):
        logging.info("Generating greetings")
        self.chat(
            prompt=INITIAL_PROMPT,
            save_user_message=False,
        )

    def chat(self, prompt, save_user_message=True):
        logging.info("Answering user prompt")
        if save_user_message:
            st.chat_message("user").write(prompt)
            self.history.append({"role": "user", "content": prompt})
        with st.chat_message(self.role):
            bot_response = self.chain.run(
                input=prompt, philosopher=self.philosopher, callbacks=self.callbacks()
            )
            self.history.append({"role": self.role, "content": bot_response})
