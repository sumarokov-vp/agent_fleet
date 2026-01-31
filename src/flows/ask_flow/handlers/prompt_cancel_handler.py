from uuid import uuid4

from bot_framework.entities.bot_callback import BotCallback
from bot_framework.language_management.repos.protocols.i_phrase_repo import IPhraseRepo
from bot_framework.protocols.i_callback_answerer import ICallbackAnswerer
from bot_framework.protocols.i_message_service import IMessageService
from bot_framework.role_management.repos.protocols.i_user_repo import IUserRepo

from src.flows.ask_flow.protocols.i_pending_prompt_storage import IPendingPromptStorage


class PromptCancelHandler:
    def __init__(
        self,
        callback_answerer: ICallbackAnswerer,
        message_service: IMessageService,
        phrase_repo: IPhraseRepo,
        user_repo: IUserRepo,
        pending_prompt_storage: IPendingPromptStorage,
    ) -> None:
        self.callback_answerer = callback_answerer
        self._message_service = message_service
        self._phrase_repo = phrase_repo
        self._user_repo = user_repo
        self._pending_prompt_storage = pending_prompt_storage
        self.prefix = uuid4().hex
        self.allowed_roles: set[str] | None = None

    def handle(self, callback: BotCallback) -> None:
        self.callback_answerer.answer(callback_query_id=callback.id)

        user = self._user_repo.get_by_id(id=callback.user_id)

        self._pending_prompt_storage.clear_pending_prompt(user.id)

        text = self._phrase_repo.get_phrase(
            key="ask.prompt_cancelled",
            language_code=user.language_code,
        )
        self._message_service.send(chat_id=user.id, text=text)
