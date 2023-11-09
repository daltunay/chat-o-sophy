from typing import List, Literal, Optional, TypedDict

BotTypeAs = Literal["philosopher", "assistant"]
PhilosopherTypeAs = Optional[str]
ProviderTypeAs = Literal["openai", "replicate"]
ModelNameTypeAs = Literal[
    "gpt-3.5-turbo", "mistral-7b-instruct-v0.1", "llama-2-7b-chat"
]
LanguageTypeAs = Literal["English", "French", "German", "Spanish"]
ModelOwnerTypeAs = Optional[Literal["mistralai", "meta"]]
ModelVersionTypeAs = Optional[str]
RoleTypeAs = Literal["ai", "human"]


class ChatHistory(TypedDict):
    role: RoleTypeAs
    content: str


ChatHistoryTypeAs = List[ChatHistory]
