from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class SessionStatus(Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    INTERRUPTED = "interrupted"
    FAILED = "failed"


class ExecutionSession(BaseModel):
    id: str
    project_id: str
    task_id: str | None = None
    working_directory: str
    status: SessionStatus = SessionStatus.ACTIVE
    started_at: datetime = Field(default_factory=datetime.now)
    ended_at: datetime | None = None
