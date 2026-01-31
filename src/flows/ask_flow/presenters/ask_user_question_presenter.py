from typing import Any

from bot_framework.entities.button import Button
from bot_framework.entities.keyboard import Keyboard
from bot_framework.language_management.repos.protocols.i_phrase_repo import IPhraseRepo
from bot_framework.protocols.i_message_service import IMessageService


class AskUserQuestionPresenter:
    def __init__(
        self,
        message_service: IMessageService,
        phrase_repo: IPhraseRepo,
    ) -> None:
        self._message_service = message_service
        self._phrase_repo = phrase_repo

    def send(
        self,
        chat_id: int,
        request_id: str,
        questions: list[dict[str, Any]],
        session_id: str,
    ) -> None:
        for question_data in questions:
            question_text = question_data.get("question", "")
            options = question_data.get("options", [])
            header = question_data.get("header", "")

            text = f"<b>{header}</b>\n\n{question_text}"

            buttons = []
            for option in options:
                label = option.get("label", "")
                callback_data = f"answer:{session_id}:{request_id}:{label}"
                if len(callback_data) > 64:
                    callback_data = callback_data[:64]
                buttons.append(Button(text=label, callback_data=callback_data))

            keyboard = Keyboard(rows=[[btn] for btn in buttons])

            self._message_service.send(
                chat_id=chat_id,
                text=text,
                keyboard=keyboard,
            )
