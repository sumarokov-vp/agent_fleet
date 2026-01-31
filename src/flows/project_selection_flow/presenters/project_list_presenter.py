from bot_framework.entities.button import Button
from bot_framework.entities.keyboard import Keyboard
from bot_framework.entities.user import User
from bot_framework.language_management.repos.protocols.i_phrase_repo import IPhraseRepo
from bot_framework.protocols.i_message_sender import IMessageSender

from src.bounded_context.project_management.entities.project import Project


class ProjectListPresenter:
    def __init__(
        self,
        message_sender: IMessageSender,
        phrase_repo: IPhraseRepo,
        project_select_handler_prefix: str,
    ) -> None:
        self._message_sender = message_sender
        self._phrase_repo = phrase_repo
        self._project_select_handler_prefix = project_select_handler_prefix

    def present(self, user: User, projects: list[Project]) -> None:
        if not projects:
            text = self._phrase_repo.get_phrase(
                key="projects.empty",
                language_code=user.language_code,
            )
            self._message_sender.send(chat_id=user.id, text=text)
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
                        text=project.id,
                        callback_data=f"{self._project_select_handler_prefix}:{project.id}",
                    )
                ]
            )

        keyboard = Keyboard(rows=buttons)
        self._message_sender.send(chat_id=user.id, text=text, keyboard=keyboard)
