import os

import requests
import streamlit as st

from utils.logging import configure_logger

logger = configure_logger(__file__)

AVAILABLE_MODELS = {
    "gpt-3.5-turbo": {"provider": "openai", "model_owner": None},
    "mistral-7b-instruct-v0.1": {"provider": "replicate", "model_owner": "mistralai"},
    "llama-2-7b-chat": {"provider": "replicate", "model_owner": "meta"},
}

API_KEYS = {
    provider: {"api_key": "", "use_default": True}
    for provider in {model_info["provider"] for model_info in AVAILABLE_MODELS.values()}
}


class APIManager:
    def __init__(self, default_provider="openai", default_model="gpt-3.5-turbo"):
        self.provider = default_provider
        self.chosen_model = default_model
        self.available_models = AVAILABLE_MODELS
        self.api_keys = API_KEYS

    def choose_model(self):
        self.chosen_model = st.selectbox(
            label="Select the model:",
            options=self.available_models.keys(),
            key="api_manager.chosen_model",
            index=list(self.available_models.keys()).index(
                st.session_state.get("api_manager.chosen_model", self.chosen_model)
            ),
            on_change=logger.info,
            kwargs={"msg": "Switching model"},
        )

        self.provider = self.available_models[self.chosen_model]["provider"]
        self.model_owner = self.available_models[self.chosen_model]["model_owner"]

    def default_api_key(self):
        self.api_keys[self.provider]["use_default"] = st.checkbox(
            label="Default API key",
            key="api_manager.use_default",
            value=st.session_state.get(
                "api_manager.use_default", self.api_keys[self.provider]["use_default"]
            ),
            help="Use the provided default API key, if you don't have any",
            on_change=logger.info,
            kwargs={"msg": "Switching default API usage"},
        )

        if self.api_keys[self.provider]["use_default"]:
            self.authenticate(
                api_key=st.secrets.get(f"{self.provider}_api").key,
                provider=self.provider,
                model_name=self.chosen_model,
                model_owner=self.model_owner,
            )

    def api_key_form(self):
        with st.form(self.provider):
            if self.provider == "openai":
                provider_label = "Enter your OpenAI API key:"
                provider_help = "Click [here](https://platform.openai.com/account/api-keys) to get your OpenAI API key"
            elif self.provider == "replicate":
                provider_label = "Enter your Replicate API key:"
                provider_help = "Click [here](https://replicate.com/account/api-tokens) to get your Replicate API key"

            self.api_keys[self.provider]["api_key"] = st.text_input(
                label=provider_label,
                value=self.api_keys[self.provider]["api_key"],
                placeholder="[default]"
                if self.api_keys[self.provider]["use_default"]
                else "",
                type="password",
                help=provider_help,
                autocomplete="",
                disabled=not self.chosen_model
                or self.api_keys[self.provider]["use_default"],
            )

            api_key = (
                st.secrets.get(f"{self.provider}_api").key
                if self.api_keys[self.provider]["use_default"]
                else self.api_keys[self.provider]["api_key"]
            )

            st.form_submit_button(
                label="Authentificate",
                on_click=self.authenticate,
                kwargs={
                    "api_key": api_key,
                    "provider": self.provider,
                    "model_name": self.chosen_model,
                    "model_owner": self.model_owner,
                },
                disabled=not self.chosen_model
                or self.api_keys[self.provider]["use_default"],
                use_container_width=True,
            )

    def authenticate(self, api_key, provider, model_name, model_owner):
        if provider == "openai":
            success = self.authenticate_openai(api_key, model_name)
        elif provider == "replicate":
            success = self.authenticate_replicate(api_key, model_owner, model_name)

        if success:
            logger.info("Authentification successful")
            st.toast(f"API Authentication successful — {provider}", icon="✅")
            self.provider = provider
            os.environ[f"{provider.upper()}_API_KEY"] = api_key
        else:
            logger.info("Authentification failed")
            st.toast(f"API Authentication failed — {provider}", icon="🚫")
            self.provider = None
            os.environ.pop(f"{provider.upper()}_API_KEY", None)

    @classmethod
    @st.cache_data(max_entries=1)
    def authenticate_openai(self, api_key, model_name):
        logger.info(msg="Requesting OpenAI API")
        response = requests.get(
            url=f"https://api.openai.com/v1/models/{model_name}",
            headers={"Authorization": f"Bearer {api_key}"},
        )
        return response.ok

    @classmethod
    @st.cache_data(max_entries=1)
    def authenticate_replicate(self, api_key, model_owner, model_name):
        logger.info(msg="Requesting Replicate API")
        response = requests.get(
            url=f"https://api.replicate.com/v1/models/{model_owner}/{model_name}",
            headers={"Authorization": f"Token {api_key}"},
        )
        return response.ok

    def main(self):
        st.title("Model Selection")
        self.choose_model()
        self.default_api_key()
        self.api_key_form()
