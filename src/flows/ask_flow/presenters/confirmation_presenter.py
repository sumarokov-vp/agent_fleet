from bot_framework.entities.button import Button
from bot_framework.entities.keyboard import Keyboard
from bot_framework.language_management.repos.protocols.i_phrase_repo import IPhraseRepo
from bot_framework.protocols.i_message_sender import IMessageSender


class ConfirmationPresenter:
    MAX_PROMPT_LENGTH = 1000

    def __init__(
        self,
        message_sender: IMessageSender,
        phrase_repo: IPhraseRepo,
        confirm_prefix: str,
        cancel_prefix: str,
    ) -> None:
        self._message_sender = message_sender
        self._phrase_repo = phrase_repo
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

        confirm_label = self._phrase_repo.get_phrase(
            key="ask.confirm_button",
            language_code=language_code,
        )
        cancel_label = self._phrase_repo.get_phrase(
            key="ask.cancel_button",
            language_code=language_code,
        )

        keyboard = Keyboard(
            rows=[
                [
                    Button(text=confirm_label, callback_data=self._confirm_prefix),
                    Button(text=cancel_label, callback_data=self._cancel_prefix),
                ]
            ]
        )

        self._message_sender.send(
            chat_id=chat_id,
            text=text,
            keyboard=keyboard,
        )
