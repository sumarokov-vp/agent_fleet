from uuid import uuid4

from bot_framework.entities.bot_callback import BotCallback
from bot_framework.language_management.repos.protocols.i_phrase_repo import IPhraseRepo
from bot_framework.protocols.i_callback_answerer import ICallbackAnswerer
from bot_framework.protocols.i_message_service import IMessageService
from bot_framework.role_management.repos.protocols.i_user_repo import IUserRepo

from src.bounded_context.project_management.repos.project_repo import ProjectRepo
from src.shared.protocols import IMessageForReplaceStorage, IProjectSelectionStateStorage


class ProjectSelectHandler:
    def __init__(
        self,
        callback_answerer: ICallbackAnswerer,
        message_service: IMessageService,
        phrase_repo: IPhraseRepo,
        project_repo: ProjectRepo,
        state_storage: IProjectSelectionStateStorage,
        message_for_replace_storage: IMessageForReplaceStorage,
        user_repo: IUserRepo,
    ) -> None:
        self.callback_answerer = callback_answerer
        self._message_service = message_service
        self._phrase_repo = phrase_repo
        self._project_repo = project_repo
        self._state_storage = state_storage
        self._message_for_replace_storage = message_for_replace_storage
        self._user_repo = user_repo
        self.prefix = uuid4().hex
        self.allowed_roles: set[str] | None = None

    def handle(self, callback: BotCallback) -> None:
        self.callback_answerer.answer(callback_query_id=callback.id)

        if not callback.data:
            raise ValueError("callback.data is required but was None")

        parts = callback.data.split(":")
        if len(parts) < 2:
            raise ValueError(f"Invalid callback data format: {callback.data}")

        project_id = parts[1]

        user = self._user_repo.get_by_id(id=callback.user_id)
        project = self._project_repo.get_by_id(project_id)

        if not project:
            return

        self._state_storage.save_selected_project(
            user_id=callback.user_id,
            project_id=project_id,
        )

        text = self._phrase_repo.get_phrase(
            key="projects.selected",
            language_code=user.language_code,
        ).format(project_name=project.id)

        stored_message = self._message_for_replace_storage.get(callback.user_id)
        if stored_message:
            self._message_service.replace(
                chat_id=callback.user_id,
                message_id=stored_message.message_id,
                text=text,
            )
            self._message_for_replace_storage.clear(callback.user_id)
        else:
            self._message_service.send(chat_id=callback.user_id, text=text)
