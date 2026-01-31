from datetime import UTC, datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


ResponseType = Literal["text", "ask_question", "plan_ready", "completed", "error"]
ClientType = Literal["bot", "taskmanager"]


class ClaudeResponse(BaseModel):
    request_id: str
    client_type: ClientType
    user_id: int
    response_type: ResponseType

    text: str | None = None
    questions: list[dict[str, Any]] | None = None
    plan_content: str | None = None
    accumulated_text: str | None = None
    session_id: str | None = None
    error_message: str | None = None

    timestamp: datetime = Field(default_factory=lambda: datetime.now(tz=UTC))
