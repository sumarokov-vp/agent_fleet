from bot_framework.entities.bot_message import BotMessage
from bot_framework.protocols.i_message_handler import IMessageHandler
from bot_framework.role_management.repos.protocols.i_user_repo import IUserRepo

from src.bounded_context.project_management.repos.project_repo import ProjectRepo
from src.flows.project_selection_flow.presenters.project_list_presenter import (
    ProjectListPresenter,
)


class ProjectListHandler(IMessageHandler):
    allowed_roles: set[str] | None = None

    def __init__(
        self,
        project_repo: ProjectRepo,
        project_list_presenter: ProjectListPresenter,
        user_repo: IUserRepo,
    ) -> None:
        self._project_repo = project_repo
        self._project_list_presenter = project_list_presenter
        self._user_repo = user_repo

    def handle(self, message: BotMessage) -> None:
        if not message.from_user:
            raise ValueError("message.from_user is required but was None")

        user = self._user_repo.get_by_id(id=message.from_user.id)
        projects = self._project_repo.get_all()
        self._project_list_presenter.present(user, projects)
