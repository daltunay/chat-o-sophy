import os

import streamlit as st

from chatbot import AssistantChatbot, PhilosopherChatbot
from sidebar import Sidebar
from utils.logging import configure_logger

logger = configure_logger(__file__)

st.set_page_config(page_title="chat-o-sophy - mutli mode", page_icon="💭")


PHILOSOPHERS = [
    os.path.splitext(filename)[0].replace("_", " ").title()
    for filename in os.listdir("philosophers")
]


def initialize_chatbot(model_name, model_provider, model_owner, model_version):
    st.empty()
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

    current_choices = st.multiselect(
        label="Philosophers:",
        placeholder="Choose several philosophers",
        options=PHILOSOPHERS,
        max_selections=5,
        default=None,
        disabled=not authentificated,
    )

    if not authentificated:
        st.error("Configure LLM in left sidebar to unlock selection", icon="🔒")
        return
    elif not current_choices:
        st.info("Select several philosophers in the above menu", icon="ℹ️")
        return

    if prompt := st.chat_input(
        placeholder="What is your question?",
        disabled=not (current_choices and authentificated),
    ):
        st.chat_message("human").markdown(prompt)
        history = [{"role": "human", "content": prompt}]
        for philosopher in current_choices:
            st.header(f"{philosopher}'s answer", divider="gray", anchor=False)
            chatbot = PhilosopherChatbot(
                philosopher=philosopher,
                model_provider=model_provider,
                model_name=chosen_model,
                model_owner=model_owner,
                model_version=model_version,
            )
            with st.chat_message("ai", avatar=chatbot.avatar):
                answer = chatbot.chat(prompt=prompt, language=selected_language)
                history.append({"role": philosopher, "content": answer})

        st.header(
            "Synthesis",
            anchor=False,
            help="Generated by an AI assistant, based on the above answers.",
            divider="gray",
        )
        assistant = AssistantChatbot(
            history=history,
            model_provider=model_provider,
            model_name=chosen_model,
            model_owner=model_owner,
            model_version=model_version,
        )
        assistant.summarize_responses(language=selected_language)
        assistant.summary_table(language=selected_language)


if __name__ == "__main__":
    main()
