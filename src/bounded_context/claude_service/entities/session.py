from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel


class Session(BaseModel):
    id: UUID
    job_id: UUID
    claude_session_id: str | None = None
    started_at: datetime
    ended_at: datetime | None = None
    input_tokens: int = 0
    output_tokens: int = 0
    cost_usd: Decimal = Decimal("0")
