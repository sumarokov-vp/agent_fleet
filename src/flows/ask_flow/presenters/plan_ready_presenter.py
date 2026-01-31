from bot_framework.entities.button import Button
from bot_framework.entities.keyboard import Keyboard
from bot_framework.language_management.repos.protocols.i_phrase_repo import IPhraseRepo
from bot_framework.protocols.i_message_service import IMessageService


class PlanReadyPresenter:
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
        plan_content: str | None,
        accumulated_text: str | None,
        session_id: str,
    ) -> None:
        content = plan_content or accumulated_text or ""

        if len(content) > 4000:
            self._send_as_document(chat_id, content, request_id, session_id)
        else:
            self._send_as_text(chat_id, content, request_id, session_id)

    def _send_as_text(
        self,
        chat_id: int,
        content: str,
        request_id: str,
        session_id: str,
    ) -> None:
        text = f"<b>Plan Ready</b>\n\n<pre>{content}</pre>"

        keyboard = self._create_keyboard(request_id, session_id)

        self._message_service.send(
            chat_id=chat_id,
            text=text,
            keyboard=keyboard,
        )

    def _send_as_document(
        self,
        chat_id: int,
        content: str,
        request_id: str,
        session_id: str,
    ) -> None:
        document_bytes = content.encode("utf-8")
        self._message_service.send_document(
            chat_id=chat_id,
            document=document_bytes,
            filename="plan.md",
        )

        keyboard = self._create_keyboard(request_id, session_id)
        self._message_service.send(
            chat_id=chat_id,
            text="What would you like to do with this plan?",
            keyboard=keyboard,
        )

    def _create_keyboard(self, request_id: str, session_id: str) -> Keyboard:
        return Keyboard(
            rows=[
                [
                    Button(
                        text="Execute Plan",
                        callback_data=f"execute_plan:{session_id}:{request_id}",
                    ),
                ],
                [
                    Button(
                        text="Cancel",
                        callback_data=f"cancel_plan:{session_id}:{request_id}",
                    ),
                ],
            ]
        )
