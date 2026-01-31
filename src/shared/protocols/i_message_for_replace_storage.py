from typing import Protocol

from bot_framework.entities.bot_message import BotMessage


class IMessageForReplaceStorage(Protocol):
    def save(self, user_id: int, message: BotMessage) -> None: ...

    def get(self, user_id: int) -> BotMessage | None: ...

    def clear(self, user_id: int) -> None: ...
