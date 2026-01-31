from bot_framework.language_management.repos.protocols.i_phrase_repo import IPhraseRepo
from bot_framework.protocols.i_callback_answerer import ICallbackAnswerer
from bot_framework.protocols.i_callback_handler_registry import (
    ICallbackHandlerRegistry,
)
from bot_framework.protocols.i_message_service import IMessageService
from bot_framework.role_management.repos.protocols.i_user_repo import IUserRepo

from src.bounded_context.project_management.repos.project_repo import ProjectRepo
from src.flows.execution_control_flow.handlers.status_callback_handler import (
    StatusCallbackHandler,
)
from src.flows.execution_control_flow.handlers.stop_callback_handler import (
    StopCallbackHandler,
)
from src.flows.execution_control_flow.presenters.status_presenter import StatusPresenter
from src.messaging import SyncMessagePublisher
from src.shared.protocols import IProjectSelectionStateStorage


class ExecutionControlFlowFactory:
    def __init__(
        self,
        callback_answerer: ICallbackAnswerer,
        message_service: IMessageService,
        phrase_repo: IPhraseRepo,
        user_repo: IUserRepo,
        project_repo: ProjectRepo,
        project_state_storage: IProjectSelectionStateStorage,
        stop_publisher: SyncMessagePublisher,
    ) -> None:
        self._callback_answerer = callback_answerer
        self._message_service = message_service
        self._phrase_repo = phrase_repo
        self._user_repo = user_repo
        self._project_repo = project_repo
        self._project_state_storage = project_state_storage
        self._stop_publisher = stop_publisher

        self._status_callback_handler: StatusCallbackHandler | None = None
        self._stop_callback_handler: StopCallbackHandler | None = None

    def _create_status_presenter(self) -> StatusPresenter:
        return StatusPresenter(
            message_service=self._message_service,
            phrase_repo=self._phrase_repo,
        )

    def get_status_callback_handler(self) -> StatusCallbackHandler:
        if self._status_callback_handler is None:
            self._status_callback_handler = StatusCallbackHandler(
                callback_answerer=self._callback_answerer,
                user_repo=self._user_repo,
                project_repo=self._project_repo,
                project_state_storage=self._project_state_storage,
                status_presenter=self._create_status_presenter(),
            )
        return self._status_callback_handler

    def get_stop_callback_handler(self) -> StopCallbackHandler:
        if self._stop_callback_handler is None:
            self._stop_callback_handler = StopCallbackHandler(
                callback_answerer=self._callback_answerer,
                message_service=self._message_service,
                phrase_repo=self._phrase_repo,
                user_repo=self._user_repo,
                project_state_storage=self._project_state_storage,
                stop_publisher=self._stop_publisher,
            )
        return self._stop_callback_handler

    def register_handlers(
        self,
        callback_registry: ICallbackHandlerRegistry,
    ) -> None:
        callback_registry.register(self.get_status_callback_handler())
        callback_registry.register(self.get_stop_callback_handler())
