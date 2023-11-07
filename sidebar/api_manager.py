import os

import requests
import streamlit as st

from utils.logging import configure_logger

logger = configure_logger(__file__)

AVAILABLE_MODELS = {
    "gpt-3.5-turbo": {
        "provider": "openai",
        "model_owner": None,
        "model_version": None,
    },
    "mistral-7b-instruct-v0.1": {
        "provider": "replicate",
        "model_owner": "mistralai",
        "model_version": "83b6a56e7c828e667f21fd596c338fd4f0039b46bcfa18d973e8e70e455fda70",
    },
    "llama-2-7b-chat": {
        "provider": "replicate",
        "model_owner": "meta",
        "model_version": "13c3cdee13ee059ab779f0291d29054dab00a47dad8261375654de5540165fb0",
    },
}

PROVIDER_FORMATS = {"openai": "OpenAI", "replicate": "Replicate"}

API_KEYS = {
    provider: {"api_key": "", "use_default": True}
    for provider in {model_info["provider"] for model_info in AVAILABLE_MODELS.values()}
}


class APIManager:
    def __init__(self, default_provider="openai", default_model="gpt-3.5-turbo"):
        self.provider = default_provider
        self.chosen_model = default_model
        self.provider_formats = PROVIDER_FORMATS
        self.available_models = AVAILABLE_MODELS
        self.api_keys = API_KEYS
        self.authentificated = False

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
        self.model_version = self.available_models[self.chosen_model]["model_version"]

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
            api_key = st.secrets.get(f"{self.provider}_api").key
        else:
            api_key = self.api_keys[self.provider]["api_key"]

        self.authenticate(
            api_key=api_key,
            provider=self.provider,
            model_name=self.chosen_model,
            model_owner=self.model_owner,
        )

    def api_key_form(self):
        with st.form(self.provider):
            if self.provider == "openai":
                provider_help = "Click [here](https://platform.openai.com/account/api-keys) to get your OpenAI API key"
            elif self.provider == "replicate":
                provider_help = "Click [here](https://replicate.com/account/api-tokens) to get your Replicate API key"

            self.api_keys[self.provider]["api_key"] = st.text_input(
                label=f"Enter your {self.provider_formats[self.provider]} API key:",
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
            st.toast(
                f"API Authentication successful — {self.provider_formats[self.provider]}",
                icon="✅",
            )
            os.environ[f"{provider.upper()}_API_KEY"] = api_key
            self.authentificated = True
        else:
            logger.info("Authentification failed")
            st.toast(
                f"API Authentication failed — {self.provider_formats[self.provider]}",
                icon="🚫",
            )
            os.environ.pop(f"{provider.upper()}_API_KEY", None)
            self.authentificated = False

    @classmethod
    @st.cache_data(max_entries=1, show_spinner=False)
    def authenticate_openai(cls, api_key, model_name):
        logger.info(msg="Requesting OpenAI API")
        response = requests.get(
            url=f"https://api.openai.com/v1/models/{model_name}",
            headers={"Authorization": f"Bearer {api_key}"},
        )
        return response.ok

    @classmethod
    @st.cache_data(max_entries=1, show_spinner=False)
    def authenticate_replicate(cls, api_key, model_owner, model_name):
        logger.info(msg="Requesting Replicate API")
        response = requests.get(
            url=f"https://api.replicate.com/v1/models/{model_owner}/{model_name}",
            headers={"Authorization": f"Token {api_key}"},
        )
        return response.ok

    def show_status(self):
        if self.authentificated:
            st.success(
                f"Successfully authenticated to {self.provider_formats[self.provider]} API",
                icon="🔐",
            )
        else:
            st.info(
                f"Please configure the {self.provider_formats[self.provider]} API above",
                icon="🔐",
            )

    def main(self):
        st.header("Model Selection", divider="gray")
        self.choose_model()
        self.default_api_key()
        self.api_key_form()
        self.show_status()
