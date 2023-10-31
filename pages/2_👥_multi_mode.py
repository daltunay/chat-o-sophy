import streamlit as st

from chatbot import AssistantChatbot, PhilosopherChatbot
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


def main():
    logger.info("Running multi mode")

    if api_key_manager := st.session_state.get("api_key_manager"):
        api_key_manager.display()

    with st.container():
        st.title("Multi mode", anchor=False)
        st.caption("Ask a question to several philosophers!")

        current_choices = st.multiselect(
            label="Philosophers:",
            placeholder="Choose several philosophers",
            options=PHILOSOPHERS,
            max_selections=5,
            default=None,
            disabled=not st.session_state.get("OPENAI_API_KEY"),
        )

    if prompt := st.chat_input(
        placeholder="What is your question?",
        disabled=not (current_choices and st.session_state.get("OPENAI_API_KEY")),
    ):
        st.chat_message("human").write(prompt)
        history = [{"role": "human", "content": prompt}]
        for philosopher in current_choices:
            st.header(philosopher, divider="gray", anchor=False)
            chatbot = PhilosopherChatbot(philosopher)
            with st.chat_message("ai"):
                with st.spinner(f"{philosopher} is writing..."):
                    answer = chatbot.chat(prompt=prompt)
                    history.append({"role": philosopher, "content": answer})

        st.header(
            "Synthesis",
            anchor=False,
            help="Generated by an AI assistant, based on the above answers.",
            divider="gray",
        )
        assistant = AssistantChatbot(history)
        assistant.summarize_responses()
        with st.spinner("Generating summary table..."):
            assistant.summary_table()


if __name__ == "__main__":
    main()
