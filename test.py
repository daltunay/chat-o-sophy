import os
from langchain.llms import Replicate

os.environ["CURL_CA_BUNDLE"] = ""

llm = Replicate(
    model="mistralai/mistral-7b-instruct-v0.1:83b6a56e7c828e667f21fd596c338fd4f0039b46bcfa18d973e8e70e455fda70",
    replicate_api_token="r8_Ez1niBpNFVqMTv5gHRbc9ROhvNsCQo93ZCsPj",
)

llm("What is life?")
