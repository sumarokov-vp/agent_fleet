import asyncio
from uuid import uuid4

from bot_framework.entities.bot_callback import BotCallback
from bot_framework.language_management.repos.protocols.i_phrase_repo import IPhraseRepo
from bot_framework.protocols.i_callback_answerer import ICallbackAnswerer
from bot_framework.protocols.i_message_service import IMessageService
from bot_framework.role_management.repos.protocols.i_user_repo import IUserRepo

from src.bounded_context.project_management.repos.project_repo import ProjectRepo
from src.flows.ask_flow.protocols.i_pending_prompt_storage import IPendingPromptStorage
from src.flows.ask_flow.services.prompt_executor import PromptExecutor


class PromptConfirmHandler:
    def __init__(
        self,
        callback_answerer: ICallbackAnswerer,
        message_service: IMessageService,
        phrase_repo: IPhraseRepo,
        user_repo: IUserRepo,
        project_repo: ProjectRepo,
        pending_prompt_storage: IPendingPromptStorage,
        prompt_executor: PromptExecutor,
    ) -> None:
        self.callback_answerer = callback_answerer
        self._message_service = message_service
        self._phrase_repo = phrase_repo
        self._user_repo = user_repo
        self._project_repo = project_repo
        self._pending_prompt_storage = pending_prompt_storage
        self._prompt_executor = prompt_executor
        self.prefix = uuid4().hex
        self.allowed_roles: set[str] | None = None

    def handle(self, callback: BotCallback) -> None:
        self.callback_answerer.answer(callback_query_id=callback.id)

        user = self._user_repo.get_by_id(id=callback.user_id)

        pending = self._pending_prompt_storage.get_pending_prompt(user.id)
        if not pending:
            text = self._phrase_repo.get_phrase(
                key="ask.prompt_expired",
                language_code=user.language_code,
            )
            self._message_service.send(chat_id=user.id, text=text)
            return

        project_id, prompt = pending
        self._pending_prompt_storage.clear_pending_prompt(user.id)

        project = self._project_repo.get_by_id(project_id)
        if not project:
            text = self._phrase_repo.get_phrase(
                key="ask.project_not_selected_hint",
                language_code=user.language_code,
            )
            self._message_service.send(chat_id=user.id, text=text)
            return

        asyncio.run(
            self._prompt_executor.execute(
                project=project,
                prompt=prompt,
                user_id=user.id,
                language_code=user.language_code,
            )
        )
