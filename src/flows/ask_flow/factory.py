from bot_framework.language_management.repos.protocols.i_phrase_repo import IPhraseRepo
from bot_framework.protocols.i_callback_answerer import ICallbackAnswerer
from bot_framework.protocols.i_callback_handler_registry import (
    ICallbackHandlerRegistry,
)
from bot_framework.protocols.i_message_service import IMessageService
from bot_framework.role_management.repos.protocols.i_user_repo import IUserRepo

from src.bounded_context.project_management.repos.project_repo import ProjectRepo
from src.flows.ask_flow.handlers.execute_plan_handler import (
    CancelPlanHandler,
    ExecutePlanHandler,
)
from src.flows.ask_flow.handlers.prompt_cancel_handler import PromptCancelHandler
from src.flows.ask_flow.handlers.prompt_confirm_handler import PromptConfirmHandler
from src.flows.ask_flow.handlers.text_message_handler import TextMessageHandler
from src.flows.ask_flow.handlers.user_answer_handler import UserAnswerHandler
from src.flows.ask_flow.presenters.confirmation_presenter import ConfirmationPresenter
from src.flows.ask_flow.presenters.execution_progress_presenter import (
    ExecutionProgressPresenter,
)
from src.flows.ask_flow.protocols.i_pending_prompt_storage import IPendingPromptStorage
from src.flows.ask_flow.services.prompt_executor import PromptExecutor
from src.messaging import SyncMessagePublisher
from src.shared.protocols import IMessageForReplaceStorage, IProjectSelectionStateStorage


class AskFlowFactory:
    def __init__(
        self,
        callback_answerer: ICallbackAnswerer,
        message_service: IMessageService,
        phrase_repo: IPhraseRepo,
        user_repo: IUserRepo,
        project_repo: ProjectRepo,
        project_state_storage: IProjectSelectionStateStorage,
        pending_prompt_storage: IPendingPromptStorage,
        message_for_replace_storage: IMessageForReplaceStorage,
        request_publisher: SyncMessagePublisher,
    ) -> None:
        self._callback_answerer = callback_answerer
        self._message_service = message_service
        self._phrase_repo = phrase_repo
        self._user_repo = user_repo
        self._project_repo = project_repo
        self._project_state_storage = project_state_storage
        self._pending_prompt_storage = pending_prompt_storage
        self._message_for_replace_storage = message_for_replace_storage
        self._request_publisher = request_publisher

        self._prompt_confirm_handler: PromptConfirmHandler | None = None
        self._prompt_cancel_handler: PromptCancelHandler | None = None
        self._user_answer_handler: UserAnswerHandler | None = None
        self._execute_plan_handler: ExecutePlanHandler | None = None
        self._cancel_plan_handler: CancelPlanHandler | None = None

    def _create_progress_presenter(self) -> ExecutionProgressPresenter:
        return ExecutionProgressPresenter(
            message_service=self._message_service,
            phrase_repo=self._phrase_repo,
            message_for_replace_storage=self._message_for_replace_storage,
        )

    def _create_prompt_executor(self) -> PromptExecutor:
        return PromptExecutor(
            request_publisher=self._request_publisher,
            progress_presenter=self._create_progress_presenter(),
        )

    def _create_confirmation_presenter(self) -> ConfirmationPresenter:
        return ConfirmationPresenter(
            message_service=self._message_service,
            phrase_repo=self._phrase_repo,
            message_for_replace_storage=self._message_for_replace_storage,
            confirm_prefix=self.get_prompt_confirm_handler().prefix,
            cancel_prefix=self.get_prompt_cancel_handler().prefix,
        )

    def get_prompt_confirm_handler(self) -> PromptConfirmHandler:
        if self._prompt_confirm_handler is None:
            self._prompt_confirm_handler = PromptConfirmHandler(
                callback_answerer=self._callback_answerer,
                message_service=self._message_service,
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
                message_service=self._message_service,
                phrase_repo=self._phrase_repo,
                user_repo=self._user_repo,
                pending_prompt_storage=self._pending_prompt_storage,
            )
        return self._prompt_cancel_handler

    def create_text_message_handler(self) -> TextMessageHandler:
        return TextMessageHandler(
            message_service=self._message_service,
            phrase_repo=self._phrase_repo,
            user_repo=self._user_repo,
            project_repo=self._project_repo,
            project_state_storage=self._project_state_storage,
            pending_prompt_storage=self._pending_prompt_storage,
            confirmation_presenter=self._create_confirmation_presenter(),
        )

    def get_user_answer_handler(self) -> UserAnswerHandler:
        if self._user_answer_handler is None:
            self._user_answer_handler = UserAnswerHandler(
                callback_answerer=self._callback_answerer,
                message_service=self._message_service,
                phrase_repo=self._phrase_repo,
                user_repo=self._user_repo,
                project_repo=self._project_repo,
                project_state_storage=self._project_state_storage,
                prompt_executor=self._create_prompt_executor(),
            )
        return self._user_answer_handler

    def get_execute_plan_handler(self) -> ExecutePlanHandler:
        if self._execute_plan_handler is None:
            self._execute_plan_handler = ExecutePlanHandler(
                callback_answerer=self._callback_answerer,
                message_service=self._message_service,
                phrase_repo=self._phrase_repo,
                user_repo=self._user_repo,
                project_repo=self._project_repo,
                project_state_storage=self._project_state_storage,
                prompt_executor=self._create_prompt_executor(),
            )
        return self._execute_plan_handler

    def get_cancel_plan_handler(self) -> CancelPlanHandler:
        if self._cancel_plan_handler is None:
            self._cancel_plan_handler = CancelPlanHandler(
                callback_answerer=self._callback_answerer,
                message_service=self._message_service,
                phrase_repo=self._phrase_repo,
                user_repo=self._user_repo,
            )
        return self._cancel_plan_handler

    def register_handlers(
        self,
        callback_registry: ICallbackHandlerRegistry,
    ) -> None:
        callback_registry.register(self.get_prompt_confirm_handler())
        callback_registry.register(self.get_prompt_cancel_handler())
        callback_registry.register(self.get_user_answer_handler())
        callback_registry.register(self.get_execute_plan_handler())
        callback_registry.register(self.get_cancel_plan_handler())
