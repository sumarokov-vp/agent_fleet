from datetime import UTC, datetime
from typing import Literal
from uuid import uuid4

from src.bounded_context.project_management.entities.project import Project
from src.flows.ask_flow.presenters.execution_progress_presenter import (
    ExecutionProgressPresenter,
)
from src.messaging import ClaudeRequest, MessagePublisher

PermissionMode = Literal["default", "acceptEdits", "plan"]


class PromptExecutor:
    def __init__(
        self,
        request_publisher: MessagePublisher,
        progress_presenter: ExecutionProgressPresenter,
    ) -> None:
        self._request_publisher = request_publisher
        self._progress_presenter = progress_presenter

    async def execute(
        self,
        project: Project,
        prompt: str,
        user_id: int,
        language_code: str,
        permission_mode: PermissionMode = "default",
        session_id: str | None = None,
        answer_to_question: dict[str, str] | None = None,
    ) -> None:
        self._progress_presenter.send_started(
            chat_id=user_id,
            language_code=language_code,
        )

        request = ClaudeRequest(
            request_id=str(uuid4()),
            client_type="bot",
            user_id=user_id,
            project_id=project.id,
            project_path=project.path,
            prompt=prompt,
            permission_mode=permission_mode,
            session_id=session_id,
            answer_to_question=answer_to_question,
            timestamp=datetime.now(tz=UTC),
        )

        await self._request_publisher.publish(
            message=request,
            routing_key="claude.request",
        )
