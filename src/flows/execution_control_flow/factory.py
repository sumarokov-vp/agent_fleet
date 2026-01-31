from bot_framework.language_management.repos.protocols.i_phrase_repo import IPhraseRepo
from bot_framework.protocols.i_message_handler_registry import IMessageHandlerRegistry
from bot_framework.protocols.i_message_sender import IMessageSender
from bot_framework.role_management.repos.protocols.i_user_repo import IUserRepo

from src.bounded_context.agent_control.services.agent_session_manager import (
    AgentSessionManager,
)
from src.bounded_context.project_management.repos.project_repo import ProjectRepo
from src.flows.execution_control_flow.handlers.status_command_handler import (
    StatusCommandHandler,
)
from src.flows.execution_control_flow.handlers.stop_command_handler import (
    StopCommandHandler,
)
from src.flows.execution_control_flow.presenters.status_presenter import StatusPresenter
from src.flows.project_selection_flow.protocols.i_project_selection_state_storage import (
    IProjectSelectionStateStorage,
)


class ExecutionControlFlowFactory:
    def __init__(
        self,
        message_sender: IMessageSender,
        phrase_repo: IPhraseRepo,
        user_repo: IUserRepo,
        project_repo: ProjectRepo,
        project_state_storage: IProjectSelectionStateStorage,
        session_manager: AgentSessionManager,
    ) -> None:
        self._message_sender = message_sender
        self._phrase_repo = phrase_repo
        self._user_repo = user_repo
        self._project_repo = project_repo
        self._project_state_storage = project_state_storage
        self._session_manager = session_manager

    def _create_status_presenter(self) -> StatusPresenter:
        return StatusPresenter(
            message_sender=self._message_sender,
            phrase_repo=self._phrase_repo,
        )

    def _create_status_command_handler(self) -> StatusCommandHandler:
        return StatusCommandHandler(
            user_repo=self._user_repo,
            project_repo=self._project_repo,
            project_state_storage=self._project_state_storage,
            session_manager=self._session_manager,
            status_presenter=self._create_status_presenter(),
        )

    def _create_stop_command_handler(self) -> StopCommandHandler:
        return StopCommandHandler(
            message_sender=self._message_sender,
            phrase_repo=self._phrase_repo,
            user_repo=self._user_repo,
            project_state_storage=self._project_state_storage,
            session_manager=self._session_manager,
        )

    def register_handlers(
        self,
        message_registry: IMessageHandlerRegistry,
    ) -> None:
        message_registry.register(
            handler=self._create_status_command_handler(),
            commands=["status"],
            content_types=["text"],
        )
        message_registry.register(
            handler=self._create_stop_command_handler(),
            commands=["stop"],
            content_types=["text"],
        )
