from bot_framework.entities.bot_message import BotMessage
from bot_framework.language_management.repos.protocols.i_phrase_repo import IPhraseRepo
from bot_framework.protocols.i_message_service import IMessageService

from src.shared.protocols import IMessageForReplaceStorage


class ExecutionProgressPresenter:
    MAX_TEXT_LENGTH = 4000

    def __init__(
        self,
        message_service: IMessageService,
        phrase_repo: IPhraseRepo,
        message_for_replace_storage: IMessageForReplaceStorage,
    ) -> None:
        self._message_service = message_service
        self._phrase_repo = phrase_repo
        self._message_for_replace_storage = message_for_replace_storage

    def send_started(self, chat_id: int, language_code: str) -> None:
        text = self._phrase_repo.get_phrase(
            key="ask.processing",
            language_code=language_code,
        )
        bot_message = self._send_or_replace(chat_id, text)
        self._message_for_replace_storage.save(chat_id, bot_message)

    def send_text(self, chat_id: int, text: str) -> None:
        if len(text) > self.MAX_TEXT_LENGTH:
            text = text[: self.MAX_TEXT_LENGTH] + "..."
        bot_message = self._send_or_replace(chat_id, text)
        self._message_for_replace_storage.save(chat_id, bot_message)

    def send_completed(self, chat_id: int, language_code: str) -> None:
        text = self._phrase_repo.get_phrase(
            key="ask.execution_completed",
            language_code=language_code,
        )
        bot_message = self._send_or_replace(chat_id, text)
        self._message_for_replace_storage.save(chat_id, bot_message)

    def send_error(self, chat_id: int, error: str) -> None:
        text = f"Error: {error}"
        bot_message = self._send_or_replace(chat_id, text)
        self._message_for_replace_storage.save(chat_id, bot_message)

    def _send_or_replace(self, chat_id: int, text: str) -> BotMessage:
        stored_message = self._message_for_replace_storage.get(chat_id)
        if stored_message:
            return self._message_service.replace(
                chat_id=chat_id,
                message_id=stored_message.message_id,
                text=text,
            )
        return self._message_service.send(chat_id=chat_id, text=text)
