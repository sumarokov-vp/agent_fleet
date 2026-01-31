from bot_framework.entities.bot_message import BotMessage
from bot_framework.language_management.repos.protocols.i_phrase_repo import IPhraseRepo
from bot_framework.protocols.i_message_handler import IMessageHandler
from bot_framework.protocols.i_message_sender import IMessageSender
from bot_framework.role_management.repos.protocols.i_user_repo import IUserRepo

from src.bounded_context.project_management.repos.project_repo import ProjectRepo
from src.flows.ask_flow.presenters.confirmation_presenter import ConfirmationPresenter
from src.flows.ask_flow.protocols.i_pending_prompt_storage import IPendingPromptStorage
from src.shared.protocols import IProjectSelectionStateStorage


class TextMessageHandler(IMessageHandler):
    allowed_roles: set[str] | None = None

    def __init__(
        self,
        message_sender: IMessageSender,
        phrase_repo: IPhraseRepo,
        user_repo: IUserRepo,
        project_repo: ProjectRepo,
        project_state_storage: IProjectSelectionStateStorage,
        pending_prompt_storage: IPendingPromptStorage,
        confirmation_presenter: ConfirmationPresenter,
    ) -> None:
        self._message_sender = message_sender
        self._phrase_repo = phrase_repo
        self._user_repo = user_repo
        self._project_repo = project_repo
        self._project_state_storage = project_state_storage
        self._pending_prompt_storage = pending_prompt_storage
        self._confirmation_presenter = confirmation_presenter

    def handle(self, message: BotMessage) -> None:
        if not message.from_user:
            raise ValueError("message.from_user is required but was None")

        user = self._user_repo.get_by_id(id=message.from_user.id)

        if not message.text:
            return

        prompt = message.text

        project_id = self._project_state_storage.get_selected_project(user.id)
        if not project_id:
            text = self._phrase_repo.get_phrase(
                key="ask.project_not_selected_hint",
                language_code=user.language_code,
            )
            self._message_sender.send(chat_id=user.id, text=text)
            return

        project = self._project_repo.get_by_id(project_id)
        if not project:
            text = self._phrase_repo.get_phrase(
                key="ask.project_not_selected_hint",
                language_code=user.language_code,
            )
            self._message_sender.send(chat_id=user.id, text=text)
            return

        self._pending_prompt_storage.save_pending_prompt(
            user_id=user.id,
            project_id=project_id,
            prompt=prompt,
        )

        self._confirmation_presenter.send_confirmation(
            chat_id=user.id,
            language_code=user.language_code,
            project_name=project.id,
            prompt=prompt,
        )
