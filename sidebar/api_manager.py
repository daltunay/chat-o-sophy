import os

import requests
import streamlit as st
import yaml

from utils.logging import configure_logger

logger = configure_logger(__file__)


with open("model_providers.yaml") as f:
    model_providers = yaml.safe_load(f)

AVAILABLE_MODELS = model_providers["AVAILABLE_MODELS"]
PROVIDER_FORMATS = model_providers["PROVIDER_FORMATS"]


class APIManager:
    def __init__(self, default_provider="openai", default_model="gpt-3.5-turbo"):
        self.provider = default_provider
        self.chosen_model = default_model
        self.authentificated = False
        self.api_keys = {
            provider: {"api_key": "", "use_default": True}
            for provider in {
                model_info["provider"] for model_info in AVAILABLE_MODELS.values()
            }
        }

    def choose_model(self):
        self.chosen_model = st.selectbox(
            label="Select the model:",
            options=AVAILABLE_MODELS.keys(),
            key="api_manager.chosen_model",
            index=list(AVAILABLE_MODELS.keys()).index(
                st.session_state.get("api_manager.chosen_model", self.chosen_model)
            ),
            on_change=logger.info,
            kwargs={"msg": "Switching model"},
        )

        self.provider = AVAILABLE_MODELS[self.chosen_model]["provider"]
        self.model_owner = AVAILABLE_MODELS[self.chosen_model]["model_owner"]
        self.model_version = AVAILABLE_MODELS[self.chosen_model]["model_version"]

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
                label=f"Enter your {PROVIDER_FORMATS[self.provider]['label']} API key:",
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
                f"API Authentication successful — {PROVIDER_FORMATS[self.provider]['label']}",
                icon="✅",
            )
            os.environ[PROVIDER_FORMATS[provider]["env_var"]] = api_key
            self.authentificated = True
        else:
            logger.info("Authentification failed")
            st.toast(
                f"API Authentication failed — {PROVIDER_FORMATS[self.provider]['label']}",
                icon="🚫",
            )
            os.environ.pop(PROVIDER_FORMATS[provider]["env_var"], None)
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
                f"Successfully authenticated to {PROVIDER_FORMATS[self.provider]['label']} API",
                icon="🔐",
            )
        else:
            st.info(
                f"Please configure the {PROVIDER_FORMATS[self.provider]['label']} API above",
                icon="🔐",
            )

    def main(self):
        st.header("Model Selection", divider="gray")
        self.choose_model()
        self.default_api_key()
        self.api_key_form()
        self.show_status()
