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

from streaming import StreamingChatCallbackHandler, StreamingStdOutCallbackHandler
from utils.logging import configure_logger

logger = configure_logger(__file__)


class Chatbot:
    def __init__(self, bot_type, philosopher, **kwargs):
        self.bot_type = bot_type
        self.philosopher = philosopher
        self._cached_template = None
        self._cached_memory = None
        self._cached_llm = None
        self._cached_chain = None
        for key, value in kwargs.items():
            setattr(self, key, value)

    @property
    def template(self):
        if self._cached_template is None:
            if self.bot_type == "assistant":
                message = "You are an assistant, of whom the purpose will be to summarize some philosophers' responses."
            elif self.bot_type == "philosopher":
                message = "You are the famous philosopher {philosopher}. Please chat with the user, impersonating {philosopher}."

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
        return [
            StreamingStdOutCallbackHandler(),
            StreamingChatCallbackHandler(),
        ]

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
    def __init__(self, philosopher, **kwargs):
        super().__init__(bot_type="philosopher", philosopher=philosopher, **kwargs)
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
    def __init__(self, history, **kwargs):
        super().__init__(philosopher=None, bot_type="assistant", **kwargs)
        self.history = history

    @property
    def history_str(self):
        return "\n\n".join(
            [
                f"{message['role']}'s response: {message['content']}"
                for message in self.history
            ]
        )

    def summarize_responses(self):
        return self.chain.run(input=self.history_str, callbacks=self.callbacks)

    def create_markdown_table(self):
        return self.chain.run(
            input="Synthesize all of this in a markdown table. Just give the markdown output.",
            callbacks=self.callbacks,
        )
