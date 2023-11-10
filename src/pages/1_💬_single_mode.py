import streamlit as st
import yaml

from src.chatbot import PhilosopherChatbot
from src.sidebar import Sidebar
from utils.logging import configure_logger

logger = configure_logger(__file__)

st.set_page_config(page_title="chat-o-sophy - multi mode", page_icon="💭")

with open("data/philosophers.yaml") as f:
    PHILOSOPHERS = yaml.safe_load(f)


def display_chat_history(chatbot, avatar):
    for message in chatbot.history:
        role, content = message["role"], message["content"]
        st.chat_message(role, avatar=avatar if role == "ai" else None).markdown(content)


def initialize_chatbot(model_name, model_provider, model_owner, model_version):
    st.session_state.chatbot = PhilosopherChatbot(
        philosopher=st.session_state.current_choice,
        model_provider=model_provider,
        model_name=model_name,
        model_owner=model_owner,
        model_version=model_version,
    )


def main():
    st.title("Single mode", anchor=False)
    st.caption("Chat with the philosopher of your choice!")

    sidebar = st.session_state.setdefault("sidebar", Sidebar())
    sidebar.show()

    authentificated = sidebar.api_manager.authentificated
    model_provider = sidebar.api_manager.model_provider
    chosen_model = sidebar.api_manager.chosen_model
    model_owner = sidebar.api_manager.model_owner
    model_version = sidebar.api_manager.model_version
    selected_language = sidebar.language_manager.selected_language

    current_choice = st.selectbox(
        label="Philosopher:",
        placeholder="Choose one philosopher",
        options=PHILOSOPHERS.keys(),
        index=None,
        key="current_choice",
        disabled=not authentificated,
        on_change=initialize_chatbot,
        kwargs={
            "model_name": chosen_model,
            "model_provider": model_provider,
            "model_owner": model_owner,
            "model_version": model_version,
        },
    )

    if not authentificated:
        st.error("Configure model in left sidebar to unlock selection", icon="🔒")
        return
    elif not current_choice:
        st.info("Select a philosopher in the above menu", icon="ℹ️")
        return

    if chatbot := st.session_state.get("chatbot"):
        avatar = f"static/avatars/{PHILOSOPHERS[chatbot.philosopher]['avatar']}"
        display_chat_history(chatbot, avatar)

        if chatbot.history == []:
            with st.chat_message("ai", avatar=avatar):
                with st.spinner(f"{current_choice} is writing..."):
                    chatbot.greet(language=selected_language)

        if prompt := st.chat_input(
            placeholder="What do you want to know?",
            disabled=not (current_choice and authentificated),
        ):
            st.chat_message("human").markdown(prompt)
            with st.chat_message("ai", avatar=avatar):
                with st.spinner(f"{current_choice} is writing..."):
                    chatbot.chat(prompt, language=selected_language)


if __name__ == "__main__":
    main()
