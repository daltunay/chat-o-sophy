import streamlit as st
import yaml

from chat_o_sophy.chatbot import PhilosopherChatbot
from chat_o_sophy.llm_guard import lakera_guard
from chat_o_sophy.sidebar import Sidebar
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
    sidebar.main()

    authentificated = sidebar.model_api_manager.authentificated
    model_provider = sidebar.model_api_manager.model_provider
    chosen_model = sidebar.model_api_manager.chosen_model
    model_owner = sidebar.model_api_manager.model_owner
    model_version = sidebar.model_api_manager.model_version
    selected_language = sidebar.language_manager.selected_language
    lakera_guard_active = sidebar.lakera_api_manager.activated

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
        avatar = f"assets/avatars/{PHILOSOPHERS[chatbot.philosopher]['avatar']}"
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

            # LAKERA GUARD
            if lakera_guard_active:
                lakera_flagged, lakera_response = lakera_guard(
                    prompt=prompt, api_key=st.secrets.get("lakera_guard_api").key
                )
                if lakera_flagged:
                    st.error("Lakera Guard detected a potentially harmful prompt", icon="🛡️")
                    st.expander("Lakera Guard API — LOGS").write(lakera_response)
                    return

            # CHATBOT ANSWER
            with st.chat_message("ai", avatar=avatar):
                with st.spinner(f"{current_choice} is writing..."):
                    chatbot.chat(prompt, language=selected_language)


if __name__ == "__main__":
    main()
