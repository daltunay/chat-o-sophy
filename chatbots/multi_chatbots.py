import streamlit as st

from utils.logging import configure_logger

from .single_chatbot import SingleChatbot

logger = configure_logger(__file__)


class MultiChatbots:
    def __init__(self, philosophers):
        logger.info(f"Initializing chatbots: {philosophers}")
        self.philosophers = philosophers
        self.chatbots = [
            SingleChatbot(philosopher=philosopher, role="name")
            for philosopher in philosophers
        ]
        self.history = []

    def ask(self, prompt):
        logger.info("Answering user question")
        st.chat_message("human").write(prompt)
        for chatbot in self.chatbots:
            st.subheader(chatbot.philosopher, divider="gray")
            chatbot.chat(prompt=prompt, save_user_message=False)
