from bot_framework.entities.bot_callback import BotCallback
from bot_framework.language_management.repos.protocols.i_phrase_repo import IPhraseRepo
from bot_framework.protocols.i_callback_answerer import ICallbackAnswerer
from bot_framework.protocols.i_message_service import IMessageService
from bot_framework.role_management.repos.protocols.i_user_repo import IUserRepo

from src.bounded_context.project_management.repos.project_repo import ProjectRepo
from src.flows.ask_flow.repos.redis_job_session_storage import RedisJobSessionStorage
from src.flows.ask_flow.services.prompt_executor import PromptExecutor
from src.shared.protocols import IProjectSelectionStateStorage


class ExecutePlanHandler:
    def __init__(
        self,
        callback_answerer: ICallbackAnswerer,
        message_service: IMessageService,
        phrase_repo: IPhraseRepo,
        user_repo: IUserRepo,
        project_repo: ProjectRepo,
        project_state_storage: IProjectSelectionStateStorage,
        job_session_storage: RedisJobSessionStorage,
        prompt_executor: PromptExecutor,
    ) -> None:
        self.callback_answerer = callback_answerer
        self._message_service = message_service
        self._phrase_repo = phrase_repo
        self._user_repo = user_repo
        self._project_repo = project_repo
        self._project_state_storage = project_state_storage
        self._job_session_storage = job_session_storage
        self._prompt_executor = prompt_executor
        self.prefix = "execute_plan"
        self.allowed_roles: set[str] | None = None

    def handle(self, callback: BotCallback) -> None:
        self.callback_answerer.answer(callback_query_id=callback.id)

        if not callback.data:
            return

        parts = callback.data.split(":")
        if len(parts) < 3:
            return

        session_id = parts[1]

        user = self._user_repo.get_by_id(id=callback.user_id)

        project_id = self._project_state_storage.get_selected_project(user.id)
        if not project_id:
            text = self._phrase_repo.get_phrase(
                key="ask.project_not_selected_hint",
                language_code=user.language_code,
            )
            self._message_service.send(chat_id=user.id, text=text)
            return

        project = self._project_repo.get_by_id(project_id)
        if not project:
            text = self._phrase_repo.get_phrase(
                key="ask.project_not_selected_hint",
                language_code=user.language_code,
            )
            self._message_service.send(chat_id=user.id, text=text)
            return

        job_id = self._job_session_storage.get_job_id(session_id)

        self._prompt_executor.execute(
            project=project,
            prompt="Execute the plan",
            user_id=user.id,
            language_code=user.language_code,
            permission_mode="acceptEdits",
            session_id=session_id,
            job_id=job_id,
        )


class CancelPlanHandler:
    def __init__(
        self,
        callback_answerer: ICallbackAnswerer,
        message_service: IMessageService,
        phrase_repo: IPhraseRepo,
        user_repo: IUserRepo,
    ) -> None:
        self.callback_answerer = callback_answerer
        self._message_service = message_service
        self._phrase_repo = phrase_repo
        self._user_repo = user_repo
        self.prefix = "cancel_plan"
        self.allowed_roles: set[str] | None = None

    def handle(self, callback: BotCallback) -> None:
        self.callback_answerer.answer(callback_query_id=callback.id)

        user = self._user_repo.get_by_id(id=callback.user_id)

        text = self._phrase_repo.get_phrase(
            key="ask.prompt_cancelled",
            language_code=user.language_code,
        )
        self._message_service.send(chat_id=user.id, text=text)
