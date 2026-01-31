from bot_framework.language_management.repos.protocols.i_phrase_repo import IPhraseRepo
from bot_framework.protocols.i_callback_answerer import ICallbackAnswerer
from bot_framework.protocols.i_callback_handler_registry import (
    ICallbackHandlerRegistry,
)
from bot_framework.protocols.i_message_replacer import IMessageReplacer
from bot_framework.protocols.i_message_sender import IMessageSender
from bot_framework.role_management.repos.protocols.i_user_repo import IUserRepo

from src.bounded_context.project_management.repos.project_repo import ProjectRepo
from src.flows.project_selection_flow.handlers.project_list_callback_handler import (
    ProjectListCallbackHandler,
)
from src.flows.project_selection_flow.handlers.project_select_handler import (
    ProjectSelectHandler,
)
from src.flows.project_selection_flow.presenters.project_list_presenter import (
    ProjectListPresenter,
)
from src.shared.protocols import IMessageForReplaceStorage, IProjectSelectionStateStorage


class ProjectSelectionFlowFactory:
    def __init__(
        self,
        callback_answerer: ICallbackAnswerer,
        message_sender: IMessageSender,
        message_replacer: IMessageReplacer,
        phrase_repo: IPhraseRepo,
        project_repo: ProjectRepo,
        state_storage: IProjectSelectionStateStorage,
        message_for_replace_storage: IMessageForReplaceStorage,
        user_repo: IUserRepo,
    ) -> None:
        self._callback_answerer = callback_answerer
        self._message_sender = message_sender
        self._message_replacer = message_replacer
        self._phrase_repo = phrase_repo
        self._project_repo = project_repo
        self._state_storage = state_storage
        self._message_for_replace_storage = message_for_replace_storage
        self._user_repo = user_repo

        self._project_select_handler: ProjectSelectHandler | None = None
        self._project_list_callback_handler: ProjectListCallbackHandler | None = None

    def get_project_select_handler(self) -> ProjectSelectHandler:
        if self._project_select_handler is None:
            self._project_select_handler = ProjectSelectHandler(
                callback_answerer=self._callback_answerer,
                message_sender=self._message_sender,
                message_replacer=self._message_replacer,
                phrase_repo=self._phrase_repo,
                project_repo=self._project_repo,
                state_storage=self._state_storage,
                message_for_replace_storage=self._message_for_replace_storage,
                user_repo=self._user_repo,
            )
        return self._project_select_handler

    def _create_project_list_presenter(self) -> ProjectListPresenter:
        project_select_handler = self.get_project_select_handler()
        return ProjectListPresenter(
            message_sender=self._message_sender,
            message_replacer=self._message_replacer,
            phrase_repo=self._phrase_repo,
            message_for_replace_storage=self._message_for_replace_storage,
            project_select_handler_prefix=project_select_handler.prefix,
        )

    def get_project_list_callback_handler(self) -> ProjectListCallbackHandler:
        if self._project_list_callback_handler is None:
            self._project_list_callback_handler = ProjectListCallbackHandler(
                callback_answerer=self._callback_answerer,
                project_repo=self._project_repo,
                project_list_presenter=self._create_project_list_presenter(),
                user_repo=self._user_repo,
            )
        return self._project_list_callback_handler

    def register_handlers(
        self,
        callback_registry: ICallbackHandlerRegistry,
    ) -> None:
        callback_registry.register(self.get_project_select_handler())
        callback_registry.register(self.get_project_list_callback_handler())
