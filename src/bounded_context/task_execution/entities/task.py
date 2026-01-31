from datetime import datetime

from pydantic import BaseModel, Field

from src.bounded_context.task_execution.entities.task_status import TaskStatus


class Task(BaseModel):
    id: str
    project_id: str
    title: str
    description: str
    status: TaskStatus
    assignee: str | None = None
    estimate_hours: float | None = None
    spent_hours: float = 0.0
    external_url: str | None = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
