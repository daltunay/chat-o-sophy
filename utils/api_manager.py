import os
import streamlit as st


class APIManager:
    def __init__(self):
        self.api_keys = {
            "baseten": {"key": "", "env_var_api_key": "BASETEN_API_KEY", "env_var_deployment_id": "BASETEN_DEPLOYMENT_ID"},
            "openai": {"key": "", "env_var_api_key": "OPENAI_API_KEY"},
        }
        self.provider = None
        self.model_choices = {
            "llama-2-7b-chat": self.baseten_api_form,
            "mistral-7b-instruct-model": self.baseten_api_form,
            "gpt3.5-turbo": self.openai_api_form,
        }
        self.valid_api_key = False

    def set_session_state(self):
        st.session_state.setdefault("use_local_api_key", False)
        st.session_state.setdefault("user_api_key_openai", "")
        st.session_state.setdefault("user_api_key_baseten", "")
        st.session_state.setdefault("user_deployment_id_baseten", "")
        st.session_state.setdefault("model_choice", "llama-2-7b-chat")

    def model_choice_selection(self):
        st.selectbox(
            label="Select the model:",
            options=("llama-2-7b-chat", "mistral-7b-instruct-model", "gpt3.5-turbo"),
            index=(
                "llama-2-7b-chat",
                "mistral-7b-instruct-model",
                "gpt3.5-turbo",
            ).index(st.session_state.model_choice),
            key="model_choice",
            on_change=self.check_api_key,
        )

    def default_api_checkbox(self):
        st.checkbox(
            label="Default API key",
            help="Use the provided default API key, if you don't have any.",
            key="use_local_api_key",
            value=st.session_state.use_local_api_key,
            on_change=self.check_api_key,
        )

    def baseten_api_form(self):
        self.api_form(
            "baseten",
            "Enter your Baseten API key:",
            "user_api_key_baseten",
            "user_deployment_id_baseten",
        )

    def openai_api_form(self):
        self.api_form("openai", "Enter your OpenAI API key:", "user_api_key_openai")

    def api_form(self, provider, label, user_key, user_deployment_key=None):
        with st.form(f"{provider}_api"):
            st.text_input(
                label=label,
                value=st.session_state[user_key],
                placeholder="...",
                type="password",
                autocomplete="",
                key=user_key,
                disabled=st.session_state.use_local_api_key,
            )
            if provider == "baseten":
                st.text_input(
                    label="Deployment ID",
                    value=st.session_state[user_deployment_key],
                    placeholder="...",
                    key=user_deployment_key,
                    disabled=st.session_state.use_local_api_key,
                )
            st.form_submit_button(
                label="Submit",
                use_container_width=True,
                disabled=st.session_state.use_local_api_key,
                on_click=lambda: self.check_api_key(provider),
            )

    def check_api_key(self, provider=None):
        if provider is None:
            provider = {
                "llama-2-7b-chat": "baseten",
                "mistral-7b-instruct-model": "baseten",
                "gpt3.5-turbo": "openai",
            }[st.session_state.model_choice]
        api_key = (
            st.secrets[f"{provider}_api"].key
            if st.session_state.use_local_api_key
            else st.session_state.get(f"user_api_key_{provider}")
        )

        deployment_id = (
            st.secrets[f"{provider}_api"].deployment_id
            if st.session_state.use_local_api_key
            else st.session_state.get(f"user_deployment_id_{provider}")
        )

        self.authenticate(provider, api_key, deployment_id)

    def authenticate(self, provider, key, deployment_id):
        try:
            if provider == "openai":
                self.authenticate_openai(key)
            elif provider == "baseten":
                self.authenticate_baseten(key, deployment_id)
            self.provider = provider
            self.store_api_key(provider, key)
            self.store_deployment_id(provider, deployment_id)
            st.toast(f"API Authentication successful — {provider}", icon="✅")

        except Exception as e:
            self.provider = None
            self.delete_api_key(provider)
            st.toast(f"API Authentication error — {provider}", icon="🚫")

    def authenticate_openai(self, key):
        import openai

        openai.api_key = key
        openai.Model.list()

    def authenticate_baseten(self, key, deployment_id):
        import requests

        response = requests.post(
            url=f"https://app.baseten.co/model_versions/{deployment_id}/wake",
            headers={"Authorization": f"Api-Key {key}"},
        )
        if not response.ok:
            raise Exception

    def store_api_key(self, provider, key):
        os.environ[self.api_keys[provider]["env_var_api_key"]] = key
        self.valid_api_key = True

    def store_deployment_id(self, provider, deployment_id):
        os.environ[self.api_keys[provider]["env_var_deployment_id"]] = deployment_id
        self.valid_deployment_id = True

    def delete_api_key(self, provider):
        os.environ.pop(self.api_keys[provider]["env_var_api_key"], None)
        self.valid_api_key = False

    def main(self):
        st.title("LLM API")
        self.set_session_state()
        self.model_choice_selection()
        self.default_api_checkbox()
        self.model_choices[st.session_state.model_choice]()


if __name__ == "__main__":
    manager = APIManager()
    manager.main()
