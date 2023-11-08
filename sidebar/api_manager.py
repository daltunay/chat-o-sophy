import os

import requests
import streamlit as st
import yaml

from utils.logging import configure_logger

logger = configure_logger(__file__)


with open("model_providers.yaml") as f:
    model_providers = yaml.safe_load(f)

MODELS = model_providers["MODELS"]
PROVIDERS = model_providers["PROVIDERS"]


class APIManager:
    def __init__(self, default_provider="openai", default_model="gpt-3.5-turbo"):
        self.provider = default_provider
        self.chosen_model = default_model
        self.authentificated = False
        self.api_keys = {
            provider: {"api_key": "", "use_default": True}
            for provider in {model_info["provider"] for model_info in MODELS.values()}
        }

    def choose_model(self):
        self.chosen_model = st.selectbox(
            label="Select the model:",
            options=MODELS.keys(),
            key="api_manager.chosen_model",
            index=list(MODELS.keys()).index(
                st.session_state.get("api_manager.chosen_model", self.chosen_model)
            ),
            on_change=logger.info,
            kwargs={"msg": "Switching model"},
        )

        self.provider = MODELS[self.chosen_model]["provider"]
        self.model_owner = MODELS[self.chosen_model]["model_owner"]
        self.model_version = MODELS[self.chosen_model]["model_version"]

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
            provider_label = PROVIDERS[self.provider]["label"]
            provider_help = PROVIDERS[self.provider]["api_help"]

            self.api_keys[self.provider]["api_key"] = st.text_input(
                label=f"Enter your {provider_label} API key:",
                value=self.api_keys[self.provider]["api_key"],
                placeholder="[default]"
                if self.api_keys[self.provider]["use_default"]
                else "",
                type="password",
                help=f"Click [here]({provider_help}) to get your {provider_label} API key",
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
        provider_label = PROVIDERS[self.provider]["label"]
        provider_env_var = PROVIDERS[provider]["env_var"]

        if provider == "openai":
            success = self.authenticate_openai(api_key, model_name)
        elif provider == "replicate":
            success = self.authenticate_replicate(api_key, model_owner, model_name)

        if success:
            logger.info("Authentification successful")
            st.toast(
                f"API Authentication successful — {provider_label}",
                icon="✅",
            )
            os.environ[provider_env_var] = api_key
            self.authentificated = True
        else:
            logger.info("Authentification failed")
            st.toast(
                f"API Authentication failed — {provider_label}",
                icon="🚫",
            )
            os.environ.pop(provider_env_var, None)
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
        provider_label = PROVIDERS[self.provider]["label"]

        if self.authentificated:
            st.success(
                f"Successfully authenticated to {provider_label} API",
                icon="🔐",
            )
        else:
            st.info(
                f"Please configure the {provider_label} API above",
                icon="🔐",
            )

    def main(self):
        st.header("Model Selection", divider="gray")
        self.choose_model()
        self.default_api_key()
        self.api_key_form()
        self.show_status()
