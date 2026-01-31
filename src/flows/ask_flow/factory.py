from bot_framework.language_management.repos.protocols.i_phrase_repo import IPhraseRepo
from bot_framework.protocols.i_callback_answerer import ICallbackAnswerer
from bot_framework.protocols.i_callback_handler_registry import (
    ICallbackHandlerRegistry,
)
from bot_framework.protocols.i_message_sender import IMessageSender
from bot_framework.role_management.repos.protocols.i_user_repo import IUserRepo

from src.bounded_context.agent_control.services.agent_session_manager import (
    AgentSessionManager,
)
from src.bounded_context.agent_control.services.project_lock_manager import (
    ProjectLockManager,
)
from src.bounded_context.project_management.repos.project_repo import ProjectRepo
from src.flows.ask_flow.handlers.prompt_cancel_handler import PromptCancelHandler
from src.flows.ask_flow.handlers.prompt_confirm_handler import PromptConfirmHandler
from src.flows.ask_flow.handlers.text_message_handler import TextMessageHandler
from src.flows.ask_flow.presenters.confirmation_presenter import ConfirmationPresenter
from src.flows.ask_flow.presenters.execution_progress_presenter import (
    ExecutionProgressPresenter,
)
from src.flows.ask_flow.protocols.i_pending_prompt_storage import IPendingPromptStorage
from src.flows.ask_flow.services.prompt_executor import PromptExecutor
from src.flows.project_selection_flow.protocols.i_project_selection_state_storage import (
    IProjectSelectionStateStorage,
)


class AskFlowFactory:
    def __init__(
        self,
        callback_answerer: ICallbackAnswerer,
        message_sender: IMessageSender,
        phrase_repo: IPhraseRepo,
        user_repo: IUserRepo,
        project_repo: ProjectRepo,
        project_state_storage: IProjectSelectionStateStorage,
        pending_prompt_storage: IPendingPromptStorage,
        lock_manager: ProjectLockManager,
        session_manager: AgentSessionManager,
    ) -> None:
        self._callback_answerer = callback_answerer
        self._message_sender = message_sender
        self._phrase_repo = phrase_repo
        self._user_repo = user_repo
        self._project_repo = project_repo
        self._project_state_storage = project_state_storage
        self._pending_prompt_storage = pending_prompt_storage
        self._lock_manager = lock_manager
        self._session_manager = session_manager

        self._prompt_confirm_handler: PromptConfirmHandler | None = None
        self._prompt_cancel_handler: PromptCancelHandler | None = None

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

    def _create_confirmation_presenter(self) -> ConfirmationPresenter:
        return ConfirmationPresenter(
            message_sender=self._message_sender,
            phrase_repo=self._phrase_repo,
            confirm_prefix=self.get_prompt_confirm_handler().prefix,
            cancel_prefix=self.get_prompt_cancel_handler().prefix,
        )

    def get_prompt_confirm_handler(self) -> PromptConfirmHandler:
        if self._prompt_confirm_handler is None:
            self._prompt_confirm_handler = PromptConfirmHandler(
                callback_answerer=self._callback_answerer,
                message_sender=self._message_sender,
                phrase_repo=self._phrase_repo,
                user_repo=self._user_repo,
                project_repo=self._project_repo,
                pending_prompt_storage=self._pending_prompt_storage,
                prompt_executor=self._create_prompt_executor(),
            )
        return self._prompt_confirm_handler

    def get_prompt_cancel_handler(self) -> PromptCancelHandler:
        if self._prompt_cancel_handler is None:
            self._prompt_cancel_handler = PromptCancelHandler(
                callback_answerer=self._callback_answerer,
                message_sender=self._message_sender,
                phrase_repo=self._phrase_repo,
                user_repo=self._user_repo,
                pending_prompt_storage=self._pending_prompt_storage,
            )
        return self._prompt_cancel_handler

    def create_text_message_handler(self) -> TextMessageHandler:
        return TextMessageHandler(
            message_sender=self._message_sender,
            phrase_repo=self._phrase_repo,
            user_repo=self._user_repo,
            project_repo=self._project_repo,
            project_state_storage=self._project_state_storage,
            pending_prompt_storage=self._pending_prompt_storage,
            confirmation_presenter=self._create_confirmation_presenter(),
        )

    def register_handlers(
        self,
        callback_registry: ICallbackHandlerRegistry,
    ) -> None:
        callback_registry.register(self.get_prompt_confirm_handler())
        callback_registry.register(self.get_prompt_cancel_handler())
