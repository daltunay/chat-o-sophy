import streamlit as st

from src.logo import new_logo
from src.sidebar import Sidebar
from utils.logging import configure_logger

logger = configure_logger(__file__)

st.set_page_config(page_title="chat-o-sophy", page_icon="💭", layout="wide")


def main():
    sidebar = st.session_state.setdefault("sidebar", Sidebar())
    sidebar.main()

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
        
        Choose from two different modes:
        - <a href="CHAT_–_single_mode" target="_self"> single mode</a>: have a one-on-one conversation with a chosen philosopher and explore their unique perspectives.
        - <a href="CHAT_–_multi_mode" target="_self"> multi mode</a>: ask a question and get answers from multiple philosophers at once, gaining a well-rounded knowledge about the subject.
        """,
            unsafe_allow_html=True,
        )

    st.header("How it works", anchor=False, divider="gray")
    _col1, _col2 = st.columns(2)
    with _col1:
        st.subheader("Single mode", anchor=False)
        st.markdown(
            """
            1. **Choose one philosopher**: Select from a list of renowned philosophers who you want to chat with.
            2. **Have them greet you**: Read about their topics of interest and main work.
            3. **Chat with them**: Have a discussion with them about anything you want.
            """
        )
    with _col2:
        st.subheader("Multi mode", anchor=False)
        st.markdown(
            """
            1. **Choose several philosophers**: Select up to 5 philosophers at once.
            2. **Ask a single question**: Ask anything you want to learn about.
            3. **Receive responses**: Enjoy the personal answer from each of the chosen philosophers.
            4. **Assistant summary**: An assistant chatbot writes a comparative summary from the different answers.
            """
        )

    st.header("About", anchor=False, divider="gray")
    st.markdown(
        """
        The app _chat-o-sophy_ harnesses the power of Large Language Models (LLM) to allow you to chat with your favorite philosophers.
        - Available **open source** model(s): [Llama-2 7B](https://ai.meta.com/llama/), [Mistral 7B](https://mistral.ai/news/announcing-mistral-7b/) (via [Replicate](https://replicate.com/))  
        - Available **closed source** model(s): [GPT-3.5](https://platform.openai.com/docs/models/gpt-3-5) (via [OpenAI](https://platform.openai.com/))
        
        Main technical stack: [Python](https://www.python.org/), [Streamlit](https://streamlit.io/), [LangChain](https://www.langchain.com/), [Lakera](https://www.lakera.ai/)
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
            help="Randomly switches to another logo (90%) or creates a new one via OpenAI API (10%)",
        )


if __name__ == "__main__":
    main()
