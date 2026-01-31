from uuid import uuid4

from bot_framework.entities.bot_callback import BotCallback
from bot_framework.language_management.repos.protocols.i_phrase_repo import IPhraseRepo
from bot_framework.protocols.i_callback_answerer import ICallbackAnswerer
from bot_framework.protocols.i_message_service import IMessageService
from bot_framework.role_management.repos.protocols.i_user_repo import IUserRepo

from src.messaging import StopRequest, SyncMessagePublisher
from src.shared.protocols import IProjectSelectionStateStorage


class StopCallbackHandler:
    def __init__(
        self,
        callback_answerer: ICallbackAnswerer,
        message_service: IMessageService,
        phrase_repo: IPhraseRepo,
        user_repo: IUserRepo,
        project_state_storage: IProjectSelectionStateStorage,
        stop_publisher: SyncMessagePublisher,
    ) -> None:
        self.callback_answerer = callback_answerer
        self._message_service = message_service
        self._phrase_repo = phrase_repo
        self._user_repo = user_repo
        self._project_state_storage = project_state_storage
        self._stop_publisher = stop_publisher
        self.prefix = uuid4().hex
        self.allowed_roles: set[str] | None = None

    def handle(self, callback: BotCallback) -> None:
        self.callback_answerer.answer(callback_query_id=callback.id)

        user = self._user_repo.get_by_id(id=callback.user_id)

        project_id = self._project_state_storage.get_selected_project(user.id)
        if not project_id:
            text = self._phrase_repo.get_phrase(
                key="stop.no_active_session",
                language_code=user.language_code,
            )
            self._message_service.send(chat_id=user.id, text=text)
            return

        self._stop_publisher.publish(
            message=StopRequest(user_id=user.id, project_id=project_id),
            routing_key="claude.stop",
        )

        text = self._phrase_repo.get_phrase(
            key="stop.session_interrupted",
            language_code=user.language_code,
        )
        self._message_service.send(chat_id=user.id, text=text)
