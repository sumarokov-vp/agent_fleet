from bot_framework.language_management.repos.protocols.i_phrase_repo import IPhraseRepo
from bot_framework.protocols.i_message_sender import IMessageSender

from claude_code_sdk import AssistantMessage, Message, TextBlock


class ExecutionProgressPresenter:
    def __init__(
        self,
        message_sender: IMessageSender,
        phrase_repo: IPhraseRepo,
    ) -> None:
        self._message_sender = message_sender
        self._phrase_repo = phrase_repo

    def send_started(self, chat_id: int, language_code: str) -> None:
        text = self._phrase_repo.get_phrase(
            key="ask.processing",
            language_code=language_code,
        )
        self._message_sender.send(chat_id=chat_id, text=text)

    def send_message(self, chat_id: int, message: Message) -> None:
        if isinstance(message, AssistantMessage):
            text_parts = []
            for block in message.content:
                if isinstance(block, TextBlock):
                    text_parts.append(block.text)
            if text_parts:
                text = "\n".join(text_parts)
                if len(text) > 4000:
                    text = text[:4000] + "..."
                self._message_sender.send(chat_id=chat_id, text=text)

    def send_completed(self, chat_id: int, language_code: str) -> None:
        text = self._phrase_repo.get_phrase(
            key="ask.execution_completed",
            language_code=language_code,
        )
        self._message_sender.send(chat_id=chat_id, text=text)
