from datetime import UTC, datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field


PermissionMode = Literal["default", "acceptEdits", "plan"]
ClientType = Literal["bot", "taskmanager"]


class ClaudeRequest(BaseModel):
    request_id: str
    client_type: ClientType
    user_id: int
    project_id: str
    project_path: str
    prompt: str
    permission_mode: PermissionMode = "default"
    session_id: str | None = None
    job_id: UUID | None = None
    answer_to_question: dict[str, str] | None = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(tz=UTC))
