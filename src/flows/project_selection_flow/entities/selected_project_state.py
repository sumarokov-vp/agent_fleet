from pydantic import BaseModel


class SelectedProjectState(BaseModel):
    user_id: int
    project_id: str
