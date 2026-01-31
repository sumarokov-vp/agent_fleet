from bot_framework.entities.button import Button
from bot_framework.entities.keyboard import Keyboard
from bot_framework.language_management.repos.protocols.i_phrase_repo import IPhraseRepo
from bot_framework.protocols.i_message_service import IMessageService

from src.shared.protocols import IMessageForReplaceStorage


class ConfirmationPresenter:
    MAX_PROMPT_LENGTH = 1000

    def __init__(
        self,
        message_service: IMessageService,
        phrase_repo: IPhraseRepo,
        message_for_replace_storage: IMessageForReplaceStorage,
        confirm_prefix: str,
        cancel_prefix: str,
    ) -> None:
        self._message_service = message_service
        self._phrase_repo = phrase_repo
        self._message_for_replace_storage = message_for_replace_storage
        self._confirm_prefix = confirm_prefix
        self._cancel_prefix = cancel_prefix

    def send_confirmation(
        self,
        chat_id: int,
        language_code: str,
        project_name: str,
        prompt: str,
    ) -> None:
        warning_text = self._phrase_repo.get_phrase(
            key="ask.confirmation_warning",
            language_code=language_code,
        ).format(project_name=project_name)

        truncated_prompt = prompt
        if len(prompt) > self.MAX_PROMPT_LENGTH:
            truncated_prompt = prompt[: self.MAX_PROMPT_LENGTH] + "..."

        text = f"{warning_text}\n\n<pre>{truncated_prompt}</pre>"

        default_label = self._phrase_repo.get_phrase(
            key="ask.mode_default",
            language_code=language_code,
        )
        accept_edits_label = self._phrase_repo.get_phrase(
            key="ask.mode_accept_edits",
            language_code=language_code,
        )
        plan_label = self._phrase_repo.get_phrase(
            key="ask.mode_plan",
            language_code=language_code,
        )
        cancel_label = self._phrase_repo.get_phrase(
            key="ask.cancel_button",
            language_code=language_code,
        )

        keyboard = Keyboard(
            rows=[
                [
                    Button(
                        text=default_label,
                        callback_data=f"{self._confirm_prefix}:default",
                    ),
                    Button(
                        text=accept_edits_label,
                        callback_data=f"{self._confirm_prefix}:accept_edits",
                    ),
                    Button(
                        text=plan_label,
                        callback_data=f"{self._confirm_prefix}:plan",
                    ),
                ],
                [
                    Button(text=cancel_label, callback_data=self._cancel_prefix),
                ],
            ]
        )

        bot_message = self._message_service.send(
            chat_id=chat_id,
            text=text,
            keyboard=keyboard,
        )
        self._message_for_replace_storage.save(chat_id, bot_message)
