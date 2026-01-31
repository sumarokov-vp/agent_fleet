from bot_framework.entities.button import Button
from bot_framework.entities.keyboard import Keyboard
from bot_framework.entities.user import User
from bot_framework.language_management.repos.protocols.i_phrase_repo import IPhraseRepo
from bot_framework.menus.start_menu.main_menu_sender import MenuButtonConfig
from bot_framework.protocols.i_message_sender import IMessageSender

from src.bounded_context.project_management.repos.project_repo import ProjectRepo
from src.flows.project_selection_flow.protocols.i_project_selection_state_storage import (
    IProjectSelectionStateStorage,
)


class WelcomeMenuSender:
    def __init__(
        self,
        message_sender: IMessageSender,
        phrase_repo: IPhraseRepo,
        project_repo: ProjectRepo,
        state_storage: IProjectSelectionStateStorage,
        buttons: list[MenuButtonConfig],
    ) -> None:
        self._message_sender = message_sender
        self._phrase_repo = phrase_repo
        self._project_repo = project_repo
        self._state_storage = state_storage
        self._buttons = buttons

    def send(self, user: User) -> None:
        project_name = self._get_or_select_project(user.id)

        text = self._phrase_repo.get_phrase(
            key="bot.start.welcome",
            language_code=user.language_code,
        ).format(project_name=project_name)

        rows = []
        for button_config in self._buttons:
            button = Button(
                text=self._phrase_repo.get_phrase(
                    key=button_config.phrase_key,
                    language_code=user.language_code,
                ),
                callback_data=button_config.handler.prefix,
            )
            rows.append([button])

        keyboard = Keyboard(rows=rows)

        self._message_sender.send(
            chat_id=user.id,
            text=text,
            keyboard=keyboard,
        )

    def _get_or_select_project(self, user_id: int) -> str:
        project_id = self._state_storage.get_selected_project(user_id)

        if project_id:
            project = self._project_repo.get_by_id(project_id)
            if project:
                return project.description or project.id

        projects = self._project_repo.get_all()
        if projects:
            first_project = projects[0]
            self._state_storage.save_selected_project(user_id, first_project.id)
            return first_project.description or first_project.id

        return "—"
