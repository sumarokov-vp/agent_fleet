from pathlib import Path

from src.bounded_context.agent_control.services.agent_session_manager import (
    AgentSessionManager,
)
from src.bounded_context.agent_control.services.project_lock_manager import (
    ProjectLockManager,
)
from src.bounded_context.project_management.repos.project_repo import ProjectRepo


class RepoCollection:
    def __init__(
        self,
        environments_path: Path,
        redis_url: str,
    ) -> None:
        self.project_repo = ProjectRepo(environments_path)
        self.lock_manager = ProjectLockManager(redis_url)
        self.session_manager = AgentSessionManager()
