from pydantic import BaseModel


class StopRequest(BaseModel):
    user_id: int
    project_id: str
