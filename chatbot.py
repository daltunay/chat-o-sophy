from functools import cached_property

from langchain.callbacks.base import BaseCallbackHandler
from langchain.chains import LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.chat_models.base import BaseChatModel
from langchain.llms import Replicate
from langchain.memory import ConversationBufferMemory
from langchain.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
    SystemMessagePromptTemplate,
)
from langchain.schema.messages import AIMessage, HumanMessage

import utils.typing as t
from utils.streaming import CustomStreamingCallbackHandlers


class Chatbot:
    def __init__(
        self,
        bot_type: t.BotTypeAs,
        philosopher: t.PhilosopherTypeAs,
        provider: t.ProviderTypeAs,
        model_name: t.ModelNameTypeAs,
        model_owner: t.ModelOwnerTypeAs,
        model_version: t.ModelVersionTypeAs,
    ) -> None:
        self.bot_type = bot_type
        self.philosopher = philosopher
        self.provider = provider
        self.model_name = model_name
        self.model_owner = model_owner
        self.model_version = model_version

    @cached_property
    def avatar(self) -> str:
        return f"philosophers/{self.philosopher.lower().replace(' ', '_')}.jpeg"

    @cached_property
    def template(self) -> ChatPromptTemplate:
        if self.bot_type == "assistant":
            system_message = (
                "You are an assistant, of whom the purpose will be to summarize some philosophers' responses to a user question. "
                "You will write a short synthesis on the question topic, opposing philosophers' views. "
                "You will use markdown syntax and formatting, with numbered multi-level headings. "
                "The title will consist in the reformulated question. "
                "You will strictly only speak in {language}."
            )
        elif self.bot_type == "philosopher":
            system_message = (
                "From now on, you are not an AI anymore. You are in fact the famous philosopher called {philosopher}. "
                "You will have a discussion with a user, which needs your philosopher's perspective. Your purpose is to enlighten them. "
                "Please chat with the user, impersonating {philosopher}. "
                "Always answer their questions, without asking anything yourself. Do not ask any questions. "
                "You will strictly only speak in {language}."
            )

        return ChatPromptTemplate.from_messages(
            [
                SystemMessagePromptTemplate.from_template(template=system_message),
                MessagesPlaceholder(variable_name="history"),
                HumanMessagePromptTemplate.from_template(template="{input}"),
                SystemMessagePromptTemplate.from_template(
                    template="Your answer in {language}:"
                ),
            ]
        )

    @cached_property
    def memory(self) -> ConversationBufferMemory:
        return ConversationBufferMemory(
            memory_key="history",
            input_key="input",
            return_messages=True,
        )

    @cached_property
    def callbacks(self) -> t.List[BaseCallbackHandler]:
        callback_handlers = CustomStreamingCallbackHandlers()
        return callback_handlers.callbacks

    @cached_property
    def llm(self) -> BaseChatModel:
        if self.provider == "openai":
            return ChatOpenAI(
                model=self.model_name,
                streaming=True,
            )
        elif self.provider == "replicate":
            return Replicate(
                model=f"{self.model_owner}/{self.model_name}:{self.model_version}",
            )

    @cached_property
    def chain(self) -> LLMChain:
        return LLMChain(
            llm=self.llm,
            memory=self.memory,
            prompt=self.template,
            verbose=True,
        )


class PhilosopherChatbot(Chatbot):
    def __init__(
        self,
        philosopher: t.PhilosopherTypeAs,
        provider: t.ProviderTypeAs,
        model_name: t.ModelNameTypeAs,
        model_owner: t.ModelOwnerTypeAs,
        model_version: t.ModelVersionTypeAs,
    ) -> None:
        super().__init__(
            bot_type="philosopher",
            provider=provider,
            philosopher=philosopher,
            model_name=model_name,
            model_owner=model_owner,
            model_version=model_version,
        )
        self.history = []

    def greet(self, language: t.LanguageTypeAs) -> str:
        return self.chat(
            prompt="I am your guest. Please present yourself, and greet me.",
            language=language,
        )

    def chat(self, prompt: str, language: t.LanguageTypeAs) -> str:
        response = self.chain.run(
            input=prompt,
            philosopher=self.philosopher,
            language=language,
            callbacks=self.callbacks,
        )
        self.update_history()
        return response

    def update_history(self) -> None:
        self.history = []
        for message in self.memory.chat_memory.messages[1:]:
            if isinstance(message, AIMessage):
                self.history.append({"role": "ai", "content": message.content})
            elif isinstance(message, HumanMessage):
                self.history.append({"role": "human", "content": message.content})


class AssistantChatbot(Chatbot):
    def __init__(
        self,
        history: t.ChatHistoryTypeAs,
        provider: t.ProviderTypeAs,
        model_name: t.ModelNameTypeAs,
        model_owner: t.ModelOwnerTypeAs,
        model_version: t.ModelVersionTypeAs,
    ):
        super().__init__(
            philosopher=None,
            provider=provider,
            bot_type="assistant",
            model_name=model_name,
            model_owner=model_owner,
            model_version=model_version,
        )
        self.history = history

    @property
    def history_str(self) -> str:
        history_str = f"Question: {self.history[0]['content']}\n\n"
        history_str += "\n\n".join(
            [
                f"\t{message['role']}'s response: {message['content']}".replace(
                    "\n", " "
                )
                for message in self.history[1:]
            ]
        )
        return history_str

    def summarize_responses(self, language: t.LanguageTypeAs) -> str:
        return self.chain.run(
            input=self.history_str,
            language=language,
            callbacks=self.callbacks,
        )

    def summary_table(self, language: t.LanguageTypeAs) -> str:
        return self.chain.run(
            input="Synthesize all of this in Markdown table format, with the main philosophers' views. "
            "Just give the Markdown table output, nothing else. Keep it concise, as this will be displayed in a table. ",
            language=language,
            callbacks=self.callbacks,
        )
