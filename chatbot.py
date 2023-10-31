from io import StringIO

import pandas as pd
from langchain.chains import LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
    SystemMessagePromptTemplate,
)
from langchain.schema.messages import AIMessage, HumanMessage

from streaming import CallbackHandlers
from utils.logging import configure_logger

logger = configure_logger(__file__)


class Chatbot:
    def __init__(self, bot_type, philosopher):
        self.bot_type = bot_type
        self.philosopher = philosopher
        self._cached_template = None
        self._cached_memory = None
        self._cached_llm = None
        self._cached_chain = None

    @property
    def template(self):
        if self._cached_template is None:
            if self.bot_type == "assistant":
                message = (
                    "You are an assistant, of whom the purpose will be to summarize some philosophers' responses to a user question. "
                    "You will write a short synthesis on the question topic, opposing philosophers' views. "
                    "You will use markdown syntax and formatting, with numbered multi-level headings."
                )
            elif self.bot_type == "philosopher":
                message = (
                    "From now on, you are not an AI anymore. You are in fact the famous philosopher called {philosopher}. "
                    "You will have a discussion with a user, which needs your philosopher's perspective. Your purpose is to enlighten them. "
                    "Please chat with the user, impersonating {philosopher}."
                )

            self._cached_template = ChatPromptTemplate.from_messages(
                [
                    SystemMessagePromptTemplate.from_template(message),
                    MessagesPlaceholder(variable_name="history"),
                    HumanMessagePromptTemplate.from_template("{input}"),
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

    @property
    def callbacks(self):
        callback_handlers = CallbackHandlers()
        return callback_handlers.callbacks

    @property
    def llm(self):
        if self._cached_llm is None:
            self._cached_llm = ChatOpenAI(
                model_name="gpt-3.5-turbo",
                streaming=True,
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
    def __init__(self, philosopher):
        super().__init__(bot_type="philosopher", philosopher=philosopher)
        self.history = []

    def greet(self):
        return self.chat(
            prompt="I am your guest. Please present yourself, and greet me."
        )

    def chat(self, prompt):
        response = self.chain.run(
            input=prompt,
            philosopher=self.philosopher,
            callbacks=self.callbacks,
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
    def __init__(self, history):
        super().__init__(philosopher=None, bot_type="assistant")
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

    def summarize_responses(self):
        return self.chain.run(input=self.history_str, callbacks=self.callbacks)

    def create_markdown_table(self):
        return self.chain.run(
            input="Synthesize all of this in a markdown table, with the main philosophers' views. "
            "Your table will include several rows and columns. No index column. "
            "Just give the markdown output, nothing else.",
            callbacks=self.callbacks,
        )

    def create_pandas_table(self):
        md_table = self.create_markdown_table()
        return AssistantChatbot.markdown_table_to_dataframe(md_table)

    @classmethod
    def markdown_table_to_dataframe(cls, md_table):
        md_io = StringIO(md_table)
        df = pd.read_table(md_io, sep="|", header=0, index_col=1, skipinitialspace=True)
        df = df.dropna(axis=1, how="all").iloc[1:]
        return df
