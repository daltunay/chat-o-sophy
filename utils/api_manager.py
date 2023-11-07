import os

import requests
import streamlit as st

AVAILABLE_MODELS = {
    "gpt-3.5-turbo": {"provider": "openai", "model_owner": None},
    "mistral-7b-instruct-v0.1": {"provider": "replicate", "model_owner": "mistralai"},
    "llama-2-7b-chat": {"provider": "replicate", "model_owner": "meta"},
}


class APIManager:
    def __init__(self, default_provider="openai", default_model="gpt-3.5-turbo"):
        self.provider = default_provider
        self.chosen_model = default_model
        self.available_models = AVAILABLE_MODELS
        self.api_keys = {
            provider: {"api_key": "", "use_default": True}
            for provider in set(
                model_info["provider"] for model_info in AVAILABLE_MODELS.values()
            )
        }

    def choose_model(self):
        self.chosen_model = st.selectbox(
            label="Select the model:",
            options=self.available_models.keys(),
            index=list(self.available_models.keys()).index(self.chosen_model),
        )

        self.provider = self.available_models[self.chosen_model]["provider"]
        self.model_owner = self.available_models[self.chosen_model]["model_owner"]

    def default_api_key(self):
        self.api_keys[self.provider]["use_default"] = st.checkbox(
            label="Default API key",
            value=self.api_keys[self.provider]["use_default"],
            help="Use the provided default API key, if you don't have any.",
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
                provider_label = "OpenAI API key:"
                provider_help = "https://platform.openai.com/account/api-keys"
            elif self.provider == "replicate":
                provider_label = "Replicate API key:"
                provider_help = "https://replicate.com/account/api-tokens"

            self.api_keys[self.provider]["api_key"] = st.text_input(
                label=provider_label,
                value=self.api_keys[self.provider]["api_key"],
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
                label="Submit",
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
            self.provider = provider
            os.environ[f"{provider.upper()}_API_KEY"] = api_key
            st.toast(f"API Authentication successful — {provider}", icon="✅")
        else:
            self.provider = None
            os.environ.pop(f"{provider.upper()}_API_KEY", None)
            st.toast(f"API Authentication error — {provider}", icon="🚫")

    def authenticate_openai(self, api_key, model_name):
        response = requests.get(
            url=f"https://api.openai.com/v1/models/{model_name}",
            headers={"Authorization": f"Bearer {api_key}"},
        )
        return response.ok

    def authenticate_replicate(self, api_key, model_owner, model_name):
        response = requests.get(
            url=f"https://api.replicate.com/v1/models/{model_owner}/{model_name}",
            headers={"Authorization": f"Token {api_key}"},
        )
        return response.ok

    def main(self):
        st.title("LLM API")
        self.choose_model()
        self.default_api_key()
        self.api_key_form()
