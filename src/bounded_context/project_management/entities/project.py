from pydantic import BaseModel


class TaskSystemConfig(BaseModel):
    adapter: str
    project_id: int | None = None
    project_key: str | None = None
    api_url: str | None = None


class Project(BaseModel):
    id: str
    description: str
    path: str
    task_system: TaskSystemConfig | None = None
