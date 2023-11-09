import streamlit as st

from sidebar import Sidebar
from utils.logging import configure_logger
from utils.logo import new_logo

logger = configure_logger(__file__)

st.set_page_config(page_title="chat-o-sophy", page_icon="💭", layout="wide")


def main():
    logger.info("Running home")

    sidebar = st.session_state.setdefault("sidebar", Sidebar())
    sidebar.show()

    col1, col2 = st.columns(spec=[0.7, 0.3], gap="large")
    with col1:
        st.title("💭 chat-o-sophy", anchor=False)
        st.write(
            "[![source code](https://img.shields.io/badge/view_source_code-gray?logo=github)](https://github.com/daltunay/chat-o-sophy)"
        )
        st.header("Chat with your favorite philosophers!", divider="gray", anchor=False)
        st.markdown(
            """
        _chat-o-sophy_ lets you engage in enlightening conversations with famous philosophers.
        
        Choose from two modes:
        - **[single mode](single_mode)**: have a one-on-one conversation with a chosen philosopher and explore their unique perspectives.
        - **[multi mode](multi_mode)**: ask a question and get answers from multiple philosophers, gaining a well-rounded perspective.
        """
        )

    st.header("How it works", anchor=False, divider="gray")
    _col1, _col2 = st.columns(2)
    with _col1:
        st.subheader("Single mode", anchor=False)
        st.markdown(
            """
            1. **Choose a philosopher**: Select from renowned philosophers.
            2. **Have them welcome you**: Read about their topics of interest.
            3. **Chat with them**: Start a conversation with anything you want.
            """
        )
    with _col2:
        st.subheader("Multi mode", anchor=False)
        st.markdown(
            """
            1. **Choose several philosophers**: Select from renowned philosophers.
            2. **Ask a question**: Ask about anything you want to learn about.
            3. **Receive responses**: Enjoy thought-provoking answers from them.
            """
        )

    st.header("About", anchor=False, divider="gray")
    st.markdown(
        """
        The app _chat-o-sophy_ harnesses the power of Large Language Models (LLM) to allow you to chat with your favorite philosophers.
        - Available open source models: [Llama-2 7B](https://ai.meta.com/llama/), [Mistral 7B](https://mistral.ai/news/announcing-mistral-7b/) (via [Replicate](https://replicate.com/))  
        - Available closed source models: [GPT-3.5](https://platform.openai.com/docs/models/gpt-3-5) (via [OpenAI](https://platform.openai.com/))
        
        Main technical stack: [Python](https://www.python.org/), [LangChain](https://www.langchain.com/), [Streamlit](https://streamlit.io/)
        """
    )

    st.divider()

    st.markdown(
        """
    <div style="text-align: center;">
        Made by Daniel Altunay<br>
        <a href="https://linkedin.com/in/daltunay"><img src="https://img.icons8.com/?id=13930&format=png"></a>
        <a href="https://github.com/daltunay"><img src="https://img.icons8.com/?id=AZOZNnY73haj&format=png"></a>
    </div>
    """,
        unsafe_allow_html=True,
    )

    with col2:
        logo = new_logo()
        st.image(logo, use_column_width=True, caption="generated by DALL·E 2")
        st.button(
            label="New logo",
            use_container_width=True,
            on_click=new_logo.clear,
            help="Switches to an already existing logo (90% proba.), "
            "or creates a new one using the OpenAI API (10% proba.)",
        )


if __name__ == "__main__":
    main()
