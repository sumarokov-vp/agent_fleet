import logging
from typing import Protocol

from src.messaging import ClaudeResponse, MessageConsumer
from src.messaging.connection import RabbitMQConnection

logger = logging.getLogger(__name__)


class IProgressPresenter(Protocol):
    def send_text(self, chat_id: int, text: str) -> None: ...
    def send_completed(self, chat_id: int, language_code: str) -> None: ...
    def send_error(self, chat_id: int, error: str) -> None: ...


class IAskQuestionPresenter(Protocol):
    def send(
        self,
        chat_id: int,
        request_id: str,
        questions: list[dict[str, object]],
        session_id: str,
    ) -> None: ...


class IPlanReadyPresenter(Protocol):
    def send(
        self,
        chat_id: int,
        request_id: str,
        plan_content: str | None,
        accumulated_text: str | None,
        session_id: str,
    ) -> None: ...


class ClaudeResponseConsumer(MessageConsumer[ClaudeResponse]):
    def __init__(
        self,
        connection: RabbitMQConnection,
        progress_presenter: IProgressPresenter,
        ask_question_presenter: IAskQuestionPresenter,
        plan_ready_presenter: IPlanReadyPresenter,
    ) -> None:
        super().__init__(
            connection=connection,
            exchange_name="claude.responses",
            queue_name="claude.responses.bot",
            routing_key="response.bot.*",
            prefetch_count=10,
        )
        self._progress_presenter = progress_presenter
        self._ask_question_presenter = ask_question_presenter
        self._plan_ready_presenter = plan_ready_presenter

    def _parse_message(self, body: bytes) -> ClaudeResponse:
        return ClaudeResponse.model_validate_json(body)

    async def _handle_message(self, response: ClaudeResponse) -> None:
        logger.info(
            "Received response %s (type: %s) for user %s",
            response.request_id,
            response.response_type,
            response.user_id,
        )

        match response.response_type:
            case "text":
                if response.text:
                    self._progress_presenter.send_text(
                        chat_id=response.user_id,
                        text=response.text,
                    )
            case "ask_question":
                if response.questions and response.session_id:
                    self._ask_question_presenter.send(
                        chat_id=response.user_id,
                        request_id=response.request_id,
                        questions=response.questions,
                        session_id=response.session_id,
                    )
            case "plan_ready":
                if response.session_id:
                    self._plan_ready_presenter.send(
                        chat_id=response.user_id,
                        request_id=response.request_id,
                        plan_content=response.plan_content,
                        accumulated_text=response.accumulated_text,
                        session_id=response.session_id,
                    )
            case "completed":
                self._progress_presenter.send_completed(
                    chat_id=response.user_id,
                    language_code="ru",
                )
            case "error":
                self._progress_presenter.send_error(
                    chat_id=response.user_id,
                    error=response.error_message or "Unknown error",
                )
