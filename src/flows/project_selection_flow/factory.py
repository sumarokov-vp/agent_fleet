from bot_framework.language_management.repos.protocols.i_phrase_repo import IPhraseRepo
from bot_framework.protocols.i_callback_answerer import ICallbackAnswerer
from bot_framework.protocols.i_callback_handler_registry import (
    ICallbackHandlerRegistry,
)
from bot_framework.protocols.i_message_handler_registry import IMessageHandlerRegistry
from bot_framework.protocols.i_message_sender import IMessageSender
from bot_framework.role_management.repos.protocols.i_user_repo import IUserRepo

from src.bounded_context.project_management.repos.project_repo import ProjectRepo
from src.flows.project_selection_flow.handlers.project_list_handler import (
    ProjectListHandler,
)
from src.flows.project_selection_flow.handlers.project_select_handler import (
    ProjectSelectHandler,
)
from src.flows.project_selection_flow.presenters.project_list_presenter import (
    ProjectListPresenter,
)
from src.flows.project_selection_flow.protocols.i_project_selection_state_storage import (
    IProjectSelectionStateStorage,
)


class ProjectSelectionFlowFactory:
    def __init__(
        self,
        callback_answerer: ICallbackAnswerer,
        message_sender: IMessageSender,
        phrase_repo: IPhraseRepo,
        project_repo: ProjectRepo,
        state_storage: IProjectSelectionStateStorage,
        user_repo: IUserRepo,
    ) -> None:
        self._callback_answerer = callback_answerer
        self._message_sender = message_sender
        self._phrase_repo = phrase_repo
        self._project_repo = project_repo
        self._state_storage = state_storage
        self._user_repo = user_repo

        self._project_select_handler: ProjectSelectHandler | None = None

    def _get_project_select_handler(self) -> ProjectSelectHandler:
        if self._project_select_handler is None:
            self._project_select_handler = ProjectSelectHandler(
                callback_answerer=self._callback_answerer,
                message_sender=self._message_sender,
                phrase_repo=self._phrase_repo,
                project_repo=self._project_repo,
                state_storage=self._state_storage,
                user_repo=self._user_repo,
            )
        return self._project_select_handler

    def _create_project_list_presenter(self) -> ProjectListPresenter:
        project_select_handler = self._get_project_select_handler()
        return ProjectListPresenter(
            message_sender=self._message_sender,
            phrase_repo=self._phrase_repo,
            project_select_handler_prefix=project_select_handler.prefix,
        )

    def _create_project_list_handler(self) -> ProjectListHandler:
        return ProjectListHandler(
            project_repo=self._project_repo,
            project_list_presenter=self._create_project_list_presenter(),
            user_repo=self._user_repo,
        )

    def register_handlers(
        self,
        callback_registry: ICallbackHandlerRegistry,
        message_registry: IMessageHandlerRegistry,
    ) -> None:
        callback_registry.register(self._get_project_select_handler())

        message_registry.register(
            handler=self._create_project_list_handler(),
            commands=["projects"],
            content_types=["text"],
        )
