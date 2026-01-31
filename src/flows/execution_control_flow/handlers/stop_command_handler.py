import asyncio

from bot_framework.entities.bot_message import BotMessage
from bot_framework.language_management.repos.protocols.i_phrase_repo import IPhraseRepo
from bot_framework.protocols.i_message_handler import IMessageHandler
from bot_framework.protocols.i_message_sender import IMessageSender
from bot_framework.role_management.repos.protocols.i_user_repo import IUserRepo

from src.bounded_context.agent_control.services.agent_session_manager import (
    AgentSessionManager,
)
from src.flows.project_selection_flow.protocols.i_project_selection_state_storage import (
    IProjectSelectionStateStorage,
)


class StopCommandHandler(IMessageHandler):
    allowed_roles: set[str] | None = None

    def __init__(
        self,
        message_sender: IMessageSender,
        phrase_repo: IPhraseRepo,
        user_repo: IUserRepo,
        project_state_storage: IProjectSelectionStateStorage,
        session_manager: AgentSessionManager,
    ) -> None:
        self._message_sender = message_sender
        self._phrase_repo = phrase_repo
        self._user_repo = user_repo
        self._project_state_storage = project_state_storage
        self._session_manager = session_manager

    def handle(self, message: BotMessage) -> None:
        if not message.from_user:
            raise ValueError("message.from_user is required but was None")

        user = self._user_repo.get_by_id(id=message.from_user.id)

        project_id = self._project_state_storage.get_selected_project(user.id)
        if not project_id:
            text = self._phrase_repo.get_phrase(
                key="stop.no_active_session",
                language_code=user.language_code,
            )
            self._message_sender.send(chat_id=user.id, text=text)
            return

        session = self._session_manager.get_session_by_project(project_id)
        if not session:
            text = self._phrase_repo.get_phrase(
                key="stop.no_active_session",
                language_code=user.language_code,
            )
            self._message_sender.send(chat_id=user.id, text=text)
            return

        asyncio.run(self._session_manager.interrupt_session(session.id))

        text = self._phrase_repo.get_phrase(
            key="stop.session_interrupted",
            language_code=user.language_code,
        )
        self._message_sender.send(chat_id=user.id, text=text)
