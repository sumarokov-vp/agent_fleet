from uuid import uuid4

from bot_framework.entities.bot_callback import BotCallback
from bot_framework.protocols.i_callback_answerer import ICallbackAnswerer
from bot_framework.role_management.repos.protocols.i_user_repo import IUserRepo

from src.bounded_context.agent_control.services.agent_session_manager import (
    AgentSessionManager,
)
from src.bounded_context.project_management.repos.project_repo import ProjectRepo
from src.flows.execution_control_flow.presenters.status_presenter import StatusPresenter
from src.shared.protocols import IProjectSelectionStateStorage


class StatusCallbackHandler:
    def __init__(
        self,
        callback_answerer: ICallbackAnswerer,
        user_repo: IUserRepo,
        project_repo: ProjectRepo,
        project_state_storage: IProjectSelectionStateStorage,
        session_manager: AgentSessionManager,
        status_presenter: StatusPresenter,
    ) -> None:
        self.callback_answerer = callback_answerer
        self._user_repo = user_repo
        self._project_repo = project_repo
        self._project_state_storage = project_state_storage
        self._session_manager = session_manager
        self._status_presenter = status_presenter
        self.prefix = uuid4().hex
        self.allowed_roles: set[str] | None = None

    def handle(self, callback: BotCallback) -> None:
        self.callback_answerer.answer(callback_query_id=callback.id)

        user = self._user_repo.get_by_id(id=callback.user_id)

        project_id = self._project_state_storage.get_selected_project(user.id)
        if not project_id:
            self._status_presenter.send_no_active_sessions(
                chat_id=user.id,
                language_code=user.language_code,
            )
            return

        project = self._project_repo.get_by_id(project_id)
        if not project:
            self._status_presenter.send_no_active_sessions(
                chat_id=user.id,
                language_code=user.language_code,
            )
            return

        session = self._session_manager.get_session_by_project(project_id)
        if not session:
            self._status_presenter.send_no_active_sessions(
                chat_id=user.id,
                language_code=user.language_code,
            )
            return

        self._status_presenter.send_session_status(
            chat_id=user.id,
            language_code=user.language_code,
            session=session,
            project=project,
        )
