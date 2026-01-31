from uuid import uuid4

from bot_framework.entities.bot_callback import BotCallback
from bot_framework.protocols.i_callback_answerer import ICallbackAnswerer
from bot_framework.role_management.repos.protocols.i_user_repo import IUserRepo

from src.bounded_context.project_management.repos.project_repo import ProjectRepo
from src.flows.project_selection_flow.presenters.project_list_presenter import (
    ProjectListPresenter,
)


class ProjectListCallbackHandler:
    def __init__(
        self,
        callback_answerer: ICallbackAnswerer,
        project_repo: ProjectRepo,
        project_list_presenter: ProjectListPresenter,
        user_repo: IUserRepo,
    ) -> None:
        self.callback_answerer = callback_answerer
        self._project_repo = project_repo
        self._project_list_presenter = project_list_presenter
        self._user_repo = user_repo
        self.prefix = uuid4().hex
        self.allowed_roles: set[str] | None = None

    def handle(self, callback: BotCallback) -> None:
        self.callback_answerer.answer(callback_query_id=callback.id)

        user = self._user_repo.get_by_id(id=callback.user_id)
        projects = self._project_repo.get_all()
        self._project_list_presenter.present(user, projects)
