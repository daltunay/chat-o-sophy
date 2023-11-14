from functools import cached_property

import yaml
from langchain.callbacks.manager import CallbackManager
from langchain.chains import LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.chat_models.base import BaseChatModel
from langchain.llms import Replicate
from langchain.memory import ConversationBufferMemory
from langchain.prompts import (ChatPromptTemplate, HumanMessagePromptTemplate,
                               MessagesPlaceholder,
                               SystemMessagePromptTemplate)
from langchain.schema.messages import AIMessage, HumanMessage

import utils.type_as as t
from src.callbacks import CustomCallbackManager

with open("data/prompts.yaml") as f:
    PROMPTS = yaml.safe_load(f)


class Chatbot:
    def __init__(
        self,
        bot_type: t.BotTypeAs,
        philosopher: t.PhilosopherTypeAs,
        model_provider: t.ProviderTypeAs,
        model_name: t.ModelNameTypeAs,
        model_owner: t.ModelOwnerTypeAs = None,
        model_version: t.ModelVersionTypeAs = None,
    ) -> None:
        self.bot_type = bot_type
        self.philosopher = philosopher
        self.model_provider = model_provider
        self.model_name = model_name
        self.model_owner = model_owner
        self.model_version = model_version

    @cached_property
    def template(self) -> ChatPromptTemplate:
        return ChatPromptTemplate.from_messages(
            [
                SystemMessagePromptTemplate.from_template(
                    PROMPTS[self.bot_type]["system_message"]
                ),
                MessagesPlaceholder(variable_name="history"),
                HumanMessagePromptTemplate.from_template("{input}"),
                SystemMessagePromptTemplate.from_template(
                    "<Your answer in {language}:>"
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

    @property
    def callback_manager(self) -> CallbackManager:
        return CustomCallbackManager()

    @cached_property
    def llm(self) -> BaseChatModel:
        if self.model_provider == "openai":
            return ChatOpenAI(
                model=self.model_name,
                streaming=True,
            )
        elif self.model_provider == "replicate":
            return Replicate(
                model=f"{self.model_owner}/{self.model_name}:{self.model_version}",
                streaming=True,
                model_kwargs={"max_length": 8192},
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
        model_provider: t.ProviderTypeAs,
        model_name: t.ModelNameTypeAs,
        model_owner: t.ModelOwnerTypeAs = None,
        model_version: t.ModelVersionTypeAs = None,
    ) -> None:
        super().__init__(
            bot_type="philosopher",
            model_provider=model_provider,
            philosopher=philosopher,
            model_name=model_name,
            model_owner=model_owner,
            model_version=model_version,
        )
        self.history: t.ChatHistoryTypeAs = []

    def greet(self, language: t.LanguageTypeAs) -> str:
        return self.chat(
            prompt=PROMPTS["philosopher"]["greetings"],
            language=language,
        )

    def chat(self, prompt: str, language: t.LanguageTypeAs) -> str:
        response = self.chain.run(
            input=prompt,
            philosopher=self.philosopher,
            language=language,
            callbacks=self.callback_manager.handlers,
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
        model_provider: t.ProviderTypeAs,
        model_name: t.ModelNameTypeAs,
        model_owner: t.ModelOwnerTypeAs,
        model_version: t.ModelVersionTypeAs,
    ):
        super().__init__(
            philosopher=None,
            model_provider=model_provider,
            bot_type="assistant",
            model_name=model_name,
            model_owner=model_owner,
            model_version=model_version,
        )
        self.history = history

    @property
    def history_str(self) -> str:
        history_str = [f"Question: {self.history[0]['content']}"]
        for message in self.history[1:]:
            content = " ".join(message["content"].split("\n"))
            response = f"\t{message['role']}'s response: {content}"
            history_str.append(response)
        return "\n\n".join(history_str)

    def summary_text(self, language: t.LanguageTypeAs) -> str:
        return self.chain.run(
            input=PROMPTS["assistant"]["summary_text"] + self.history_str,
            language=language,
            callbacks=self.callbacks,
        )

    def summary_table(self, language: t.LanguageTypeAs) -> str:
        return self.chain.run(
            input=PROMPTS["assistant"]["summary_table"],
            language=language,
            callbacks=self.callbacks,
        )
