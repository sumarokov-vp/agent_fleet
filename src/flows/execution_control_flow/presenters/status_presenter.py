from bot_framework.language_management.repos.protocols.i_phrase_repo import IPhraseRepo
from bot_framework.protocols.i_message_service import IMessageService

from src.bounded_context.project_management.entities.project import Project


class StatusPresenter:
    def __init__(
        self,
        message_service: IMessageService,
        phrase_repo: IPhraseRepo,
    ) -> None:
        self._message_service = message_service
        self._phrase_repo = phrase_repo

    def send_no_active_sessions(self, chat_id: int, language_code: str) -> None:
        text = self._phrase_repo.get_phrase(
            key="status.no_active_sessions",
            language_code=language_code,
        )
        self._message_service.send(chat_id=chat_id, text=text)

    def send_selected_project(
        self,
        chat_id: int,
        language_code: str,
        project: Project,
    ) -> None:
        text = self._phrase_repo.get_phrase(
            key="status.selected_project",
            language_code=language_code,
        ).format(project_name=project.id)
        self._message_service.send(chat_id=chat_id, text=text)
