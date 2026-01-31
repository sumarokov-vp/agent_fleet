from bot_framework.entities.bot_message import BotMessage
from bot_framework.entities.button import Button
from bot_framework.entities.keyboard import Keyboard
from bot_framework.entities.user import User
from bot_framework.language_management.repos.protocols.i_phrase_repo import IPhraseRepo
from bot_framework.protocols.i_message_service import IMessageService

from src.bounded_context.project_management.entities.project import Project
from src.shared.protocols import IMessageForReplaceStorage


class ProjectListPresenter:
    def __init__(
        self,
        message_service: IMessageService,
        phrase_repo: IPhraseRepo,
        message_for_replace_storage: IMessageForReplaceStorage,
        project_select_handler_prefix: str,
    ) -> None:
        self._message_service = message_service
        self._phrase_repo = phrase_repo
        self._message_for_replace_storage = message_for_replace_storage
        self._project_select_handler_prefix = project_select_handler_prefix

    def present(self, user: User, projects: list[Project]) -> None:
        if not projects:
            text = self._phrase_repo.get_phrase(
                key="projects.empty",
                language_code=user.language_code,
            )
            bot_message = self._send_or_replace(user.id, text)
            self._message_for_replace_storage.save(user.id, bot_message)
            return

        text = self._phrase_repo.get_phrase(
            key="projects.title",
            language_code=user.language_code,
        )

        buttons = []
        for project in projects:
            buttons.append(
                [
                    Button(
                        text=project.description or project.id,
                        callback_data=f"{self._project_select_handler_prefix}:{project.id}",
                    )
                ]
            )

        keyboard = Keyboard(rows=buttons)
        bot_message = self._send_or_replace(user.id, text, keyboard)
        self._message_for_replace_storage.save(user.id, bot_message)

    def _send_or_replace(
        self,
        chat_id: int,
        text: str,
        keyboard: Keyboard | None = None,
    ) -> BotMessage:
        stored_message = self._message_for_replace_storage.get(chat_id)
        if stored_message:
            return self._message_service.replace(
                chat_id=chat_id,
                message_id=stored_message.message_id,
                text=text,
                keyboard=keyboard,
            )
        return self._message_service.send(chat_id=chat_id, text=text, keyboard=keyboard)
