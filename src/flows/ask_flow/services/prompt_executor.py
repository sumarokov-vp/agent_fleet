from datetime import UTC, datetime
from typing import Literal
from uuid import UUID, uuid4

from src.bounded_context.claude_service.entities.job import Job, JobStatus
from src.bounded_context.claude_service.repos.job_repo import JobRepo
from src.bounded_context.project_management.entities.project import Project
from src.flows.ask_flow.presenters.execution_progress_presenter import (
    ExecutionProgressPresenter,
)
from src.messaging import ClaudeRequest, SyncMessagePublisher

PermissionMode = Literal["default", "acceptEdits", "plan"]


class PromptExecutor:
    def __init__(
        self,
        request_publisher: SyncMessagePublisher,
        progress_presenter: ExecutionProgressPresenter,
        job_repo: JobRepo,
    ) -> None:
        self._request_publisher = request_publisher
        self._progress_presenter = progress_presenter
        self._job_repo = job_repo

    def execute(
        self,
        project: Project,
        prompt: str,
        user_id: int,
        language_code: str,
        permission_mode: PermissionMode = "default",
        session_id: str | None = None,
        job_id: UUID | None = None,
        answer_to_question: dict[str, str] | None = None,
    ) -> None:
        self._progress_presenter.send_started(
            chat_id=user_id,
            language_code=language_code,
        )

        if session_id is None:
            job = Job(
                id=uuid4(),
                project_id=project.id,
                status=JobStatus.PENDING,
                created_at=datetime.now(tz=UTC),
            )
            self._job_repo.create(job)
            job_id = job.id

        request = ClaudeRequest(
            request_id=str(uuid4()),
            client_type="bot",
            user_id=user_id,
            project_id=project.id,
            project_path=project.path,
            prompt=prompt,
            permission_mode=permission_mode,
            session_id=session_id,
            job_id=job_id,
            answer_to_question=answer_to_question,
            timestamp=datetime.now(tz=UTC),
        )

        self._request_publisher.publish(
            message=request,
            routing_key="claude.request",
        )
