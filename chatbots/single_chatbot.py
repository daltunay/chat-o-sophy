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

from utils.logging import configure_logger
from utils.streaming import StreamingChatCallbackHandler, StreamingStdOutCallbackHandler

logger = configure_logger(__file__)

INITIAL_PROMPT = "I am your guest. Please present yourself, greet me, and explain me the main topics you are interested in as a philosopher. Keep it very short."


class SingleChatbot:
    def __init__(self, philosopher):
        logger.info(f"Initializing chatbot: {philosopher}")
        self.philosopher = philosopher
        self.history = []
        self._cached_template = None
        self._cached_memory = None
        self._cached_llm = None
        self._cached_chain = None

    def __str__(self):
        return f"Chatbot: {self.philosopher}"

    def __repr__(self):
        return f"SingleChatbot(philosopher='{self.philosopher}')"

    @property
    def template(self):
        logger.info("Initializing template")
        if self._cached_template is None:
            self._cached_template = ChatPromptTemplate.from_messages(
                [
                    SystemMessagePromptTemplate.from_template(
                        "You are {philosopher}, the philosopher."
                    ),
                    MessagesPlaceholder(variable_name="history"),
                    HumanMessagePromptTemplate.from_template("{input}"),
                ]
            )
        return self._cached_template

    @property
    def memory(self):
        logger.info("Initializing memory")
        if self._cached_memory is None:
            self._cached_memory = ConversationBufferMemory(
                memory_key="history",
                input_key="input",
                return_messages=True,
            )
        return self._cached_memory

    @property
    def callbacks(self):
        logger.info("Initializing callbacks")
        return [
            StreamingStdOutCallbackHandler(),
            StreamingChatCallbackHandler(),
        ]

    @property
    def llm(self):
        logger.info("Initializing LLM")
        if self._cached_llm is None:
            self._cached_llm = ChatOpenAI(
                model_name="gpt-3.5-turbo",
                streaming=True,
            )
        return self._cached_llm

    @property
    def chain(self):
        logger.info("Initializing chain")
        if self._cached_chain is None:
            self._cached_chain = LLMChain(
                llm=self.llm,
                memory=self.memory,
                prompt=self.template,
                verbose=True,
            )
        return self._cached_chain

    def greet(self):
        logger.info("Generating greetings")
        self.greeted = True
        return self.chat(prompt=INITIAL_PROMPT)

    def chat(self, prompt):
        logger.info("Answering user prompt")
        response = self.chain.run(
            input=prompt,
            philosopher=self.philosopher,
            callbacks=self.callbacks,
        )
        self.update_history()
        return response

    def update_history(self):
        self.history = []
        for message in self.memory.chat_memory.messages:
            if isinstance(message, AIMessage):
                self.history.append({"role": "assistant", "content": message.content})
            elif isinstance(message, HumanMessage):
                self.history.append({"role": "user", "content": message.content})
