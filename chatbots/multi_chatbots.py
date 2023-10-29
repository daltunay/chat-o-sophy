import logging

import streamlit as st

from .single_chatbot import SingleChatbot


class MultiChatbots:
    def __init__(self, philosophers):
        logging.info(f"Initializing chatbots: {philosophers}")
        self.philosophers = philosophers
        self.chatbots = [
            SingleChatbot(philosopher=philosopher, role="name")
            for philosopher in philosophers
        ]
        self.history = []

    def ask(self, prompt):
        st.chat_message("user").write(prompt)
        for chatbot in self.chatbots:
            st.subheader(chatbot.philosopher, divider="gray")
            chatbot.chat(prompt=prompt, save_user_message=False)
