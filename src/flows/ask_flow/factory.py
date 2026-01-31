from bot_framework.language_management.repos.protocols.i_phrase_repo import IPhraseRepo
from bot_framework.protocols.i_message_sender import IMessageSender
from bot_framework.role_management.repos.protocols.i_user_repo import IUserRepo

from src.bounded_context.agent_control.services.agent_session_manager import (
    AgentSessionManager,
)
from src.bounded_context.agent_control.services.project_lock_manager import (
    ProjectLockManager,
)
from src.bounded_context.project_management.repos.project_repo import ProjectRepo
from src.flows.ask_flow.handlers.text_message_handler import TextMessageHandler
from src.flows.ask_flow.presenters.execution_progress_presenter import (
    ExecutionProgressPresenter,
)
from src.flows.ask_flow.services.prompt_executor import PromptExecutor
from src.flows.project_selection_flow.protocols.i_project_selection_state_storage import (
    IProjectSelectionStateStorage,
)


class AskFlowFactory:
    def __init__(
        self,
        message_sender: IMessageSender,
        phrase_repo: IPhraseRepo,
        user_repo: IUserRepo,
        project_repo: ProjectRepo,
        project_state_storage: IProjectSelectionStateStorage,
        lock_manager: ProjectLockManager,
        session_manager: AgentSessionManager,
    ) -> None:
        self._message_sender = message_sender
        self._phrase_repo = phrase_repo
        self._user_repo = user_repo
        self._project_repo = project_repo
        self._project_state_storage = project_state_storage
        self._lock_manager = lock_manager
        self._session_manager = session_manager

    def _create_progress_presenter(self) -> ExecutionProgressPresenter:
        return ExecutionProgressPresenter(
            message_sender=self._message_sender,
            phrase_repo=self._phrase_repo,
        )

    def _create_prompt_executor(self) -> PromptExecutor:
        return PromptExecutor(
            lock_manager=self._lock_manager,
            session_manager=self._session_manager,
            progress_presenter=self._create_progress_presenter(),
        )

    def create_text_message_handler(self) -> TextMessageHandler:
        return TextMessageHandler(
            message_sender=self._message_sender,
            phrase_repo=self._phrase_repo,
            user_repo=self._user_repo,
            project_repo=self._project_repo,
            project_state_storage=self._project_state_storage,
            prompt_executor=self._create_prompt_executor(),
        )
