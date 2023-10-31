import os

import openai
import streamlit as st

from utils.logging import configure_logger

logger = configure_logger(__file__)


@st.cache_resource(show_spinner="Generating logo...")
def generate_logo():
    logger.info("Generating logo")
    image = openai.Image.create(
        prompt="Picture a photo, showing a pondering robot with a lightbulb over its head. "
        "It is wearing glasses, and is reading a book. It has a mustache, and looks like a philosopher.",
        n=1,
        size="512x512",
        api_key=os.getenv("LOCAL_OPENAI_API_KEY"),
    )
    return image["data"][0]["url"]
