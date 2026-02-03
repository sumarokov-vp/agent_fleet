from datetime import datetime
from decimal import Decimal
from enum import Enum
from uuid import UUID

from pydantic import BaseModel


class JobStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class Job(BaseModel):
    id: UUID
    external_task_id: str | None = None
    project_id: str
    status: JobStatus = JobStatus.PENDING
    created_at: datetime
    completed_at: datetime | None = None
    total_input_tokens: int = 0
    total_output_tokens: int = 0
    total_cost_usd: Decimal = Decimal("0")
    total_sessions: int = 0
