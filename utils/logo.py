import os
import streamlit as st

import openai


@st.cache_resource(show_spinner="Generating logo...")
def generate_logo():
    image = openai.Image.create(
        prompt="A logo representing a cartoon robot with a mustache, wearing glasses and holding a book."
        "The robot has a thought bubble above its head containing a lightbulb symbolizing ideas and knowledge."
        "This logo is designed for a chatbot philosophy application.",
        n=1,
        size="512x512",
        api_key=os.getenv("LOCAL_OPENAI_API_KEY"),
    )
    return image["data"][0]["url"]
