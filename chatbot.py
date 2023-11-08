import os

from langchain.chains import LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.llms import Replicate
from langchain.memory import ConversationBufferMemory
from langchain.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
    SystemMessagePromptTemplate,
)
from langchain.schema.messages import AIMessage, HumanMessage

from utils.streaming import CallbackHandlers


class Chatbot:
    def __init__(
        self, bot_type, philosopher, provider, model_name, model_owner, model_version
    ):
        self.bot_type = bot_type
        self.philosopher = philosopher
        self.provider = provider
        self.model_name = model_name
        self.model_owner = model_owner
        self.model_version = model_version
        self._cached_avatar = None
        self._cached_template = None
        self._cached_memory = None
        self._cached_llm = None
        self._cached_chain = None

    @property
    def avatar(self):
        if self._cached_avatar is None:
            self._cached_avatar = (
                f"philosophers/{self.philosopher.lower().replace(' ', '_')}.jpeg"
            )
        return self._cached_avatar

    @property
    def template(self):
        if self._cached_template is None:
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

            self._cached_template = ChatPromptTemplate.from_messages(
                [
                    SystemMessagePromptTemplate.from_template(template=system_message),
                    MessagesPlaceholder(variable_name="history"),
                    HumanMessagePromptTemplate.from_template(template="{input}"),
                    SystemMessagePromptTemplate.from_template(
                        template="Your answer in {language}:"
                    ),
                ]
            )
        return self._cached_template

    @property
    def memory(self):
        if self._cached_memory is None:
            self._cached_memory = ConversationBufferMemory(
                memory_key="history",
                input_key="input",
                return_messages=True,
            )
        return self._cached_memory

    def callbacks(self):
        callback_handlers = CallbackHandlers()
        return callback_handlers.callbacks

    @property
    def llm(self):
        if self._cached_llm is None:
            if self.provider == "openai":
                self._cached_llm = ChatOpenAI(
                    model_name=self.model_name,
                    streaming=True,
                    openai_api_key=os.getenv("OPENAI_API_KEY"),
                )
            elif self.provider == "replicate":
                self._cached_llm = Replicate(
                    model=f"{self.model_owner}/{self.model_name}:{self.model_version}",
                    replicate_api_token=os.getenv("REPLICATE_API_KEY"),
                )
        return self._cached_llm

    @property
    def chain(self):
        if self._cached_chain is None:
            self._cached_chain = LLMChain(
                llm=self.llm,
                memory=self.memory,
                prompt=self.template,
                verbose=True,
            )
        return self._cached_chain


class PhilosopherChatbot(Chatbot):
    def __init__(self, philosopher, provider, model_name, model_owner, model_version):
        super().__init__(
            bot_type="philosopher",
            provider=provider,
            philosopher=philosopher,
            model_name=model_name,
            model_owner=model_owner,
            model_version=model_version,
        )
        self.history = []

    def greet(self, language):
        return self.chat(
            prompt="I am your guest. Please present yourself, and greet me.",
            language=language,
        )

    def chat(self, prompt, language):
        response = self.chain.run(
            input=prompt,
            philosopher=self.philosopher,
            language=language,
            callbacks=self.callbacks(),
        )
        self.update_history()
        return response

    def update_history(self):
        self.history = []
        for message in self.memory.chat_memory.messages[1:]:
            if isinstance(message, AIMessage):
                self.history.append({"role": "ai", "content": message.content})
            elif isinstance(message, HumanMessage):
                self.history.append({"role": "human", "content": message.content})


class AssistantChatbot(Chatbot):
    def __init__(self, history, provider, model_name, model_owner, model_version):
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
    def history_str(self):
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

    def summarize_responses(self, language):
        return self.chain.run(
            input=self.history_str, language=language, callbacks=self.callbacks()
        )

    def summary_table(self, language):
        return self.chain.run(
            input="Synthesize all of this in Markdown table format, with the main philosophers' views. "
            "Just give the Markdown table output, nothing else. Keep it concise, as this will be displayed in a table. ",
            language=language,
            callbacks=self.callbacks(),
        )
