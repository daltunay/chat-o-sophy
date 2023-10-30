import streamlit as st

from chatbot import PhilosopherChatbot
from history import display_chat_history
from utils.logging import configure_logger

logger = configure_logger(__file__)

st.set_page_config(page_title="chat-o-sophy", page_icon="💭")


PHILOSOPHERS = [
    "Plato",
    "Aristotle",
    "Socrates",
    "Confucius",
    "Immanuel Kant",
    "René Descartes",
    "David Hume",
    "John Locke",
    "Friedrich Nietzsche",
    "Thomas Aquinas",
    "Jean-Jacques Rousseau",
    "Baruch Spinoza",
    "Ludwig Wittgenstein",
    "Søren Kierkegaard",
    "Voltaire",
    "John Stuart Mill",
    "Karl Marx",
    "George Berkeley",
    "Arthur Schopenhauer",
    "G.W.F. Hegel",
]


@st.cache_resource
def initialize_single_mode():
    logger.info("Initializing single mode")
    single_mode = {
        "header_container": st.empty(),
        "current_choice": None,
        "chatbots": {},
    }
    for philosopher in PHILOSOPHERS:
        single_mode["chatbots"][philosopher] = PhilosopherChatbot(philosopher)

    return single_mode


st.session_state.single_mode = initialize_single_mode()


@display_chat_history
def main():
    logger.info("Running single mode")

    if api_key_manager := st.session_state.get("api_key_manager"):
        api_key_manager.display_api_form()

    with st.session_state.single_mode["header_container"].container():
        st.title("Single mode", anchor=False)
        st.caption("Chat with the philosopher of your choice!")

        st.session_state.single_mode["current_choice"] = st.selectbox(
            label="Philosopher:",
            placeholder="Choose one philosopher",
            options=PHILOSOPHERS,
            index=None,
            disabled=not st.session_state.get("OPENAI_API_KEY"),
        )

    if current_choice := st.session_state.single_mode["current_choice"]:
        logger.info(f"Switching to {current_choice}")
        chatbot = st.session_state.single_mode["chatbots"][current_choice]
        if chatbot.history == []:
            with st.chat_message("ai"):
                chatbot.greet()

    if prompt := st.chat_input(
        placeholder="What do you want to know?",
        disabled=not (
            st.session_state.single_mode["current_choice"]
            and st.session_state.get("OPENAI_API_KEY")
        ),
    ):
        st.chat_message("human").write(prompt)
        with st.chat_message("ai"):
            chatbot.chat(prompt)


if __name__ == "__main__":
    main()
