import streamlit as st

# import os
# import utils
#
# utils.api_key.configure_openai_api_key(home=True)
# if os.environ["OPENAI_API_KEY"]:
#     image = openai.Image.create(prompt="A chatbot philosopher", n=1, size="512x512")
#     image_url = image["data"][0]["url"]

st.set_page_config(page_title="chat-o-sophy", page_icon="💬", layout="wide")

st.sidebar.title("chat-o-sophy")

st.title("chat-o-sophy")
st.write(
    "[![View Source Code](https://img.shields.io/badge/GitHub-source_code-blue)]"
    "(https://github.com/)"
)

st.markdown("---")

st.header("Chat with your favorite philosophers!")
st.markdown(
    """
    _chat-o-sophy_ lets you engage in enlightening conversations with famous philosophers.
    
    Choose from two modes:
    - **single mode**: have a one-on-one conversation with a chosen philosopher and explore their unique perspectives.
    - **multi mode**: ask a question and get answers from multiple philosophers, gaining a well-rounded perspective.
    """
)

st.markdown("---")

st.header("How it works")
col1, col2 = st.columns(2)
with col1:
    st.subheader("Single mode")
    st.markdown(
        """
        1. **Choose a philosopher**: Select from renowned philosophers.
        2. **Have them welcome you**: Read about their topics of interest.
        3. **Chat with them**: Start a conversation with anything you want.
        """
    )
with col2:
    st.subheader("Multi mode")
    st.markdown(
        """
        1. **Choose several philosophers**: Select from renowned philosophers.
        2. **Ask a question**: Ask about anything you want to learn about.
        3. **Receive responses**: Enjoy thought-provoking answers from them.
        """
    )

st.markdown("---")

st.header("About")
st.markdown(
    """
    _chat-o-sophy_ uses Large Language Models from `langchain` library.
    """
)
