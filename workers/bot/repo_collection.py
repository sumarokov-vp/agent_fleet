from pathlib import Path

from src.bounded_context.agent_control.services.agent_session_manager import (
    AgentSessionManager,
)
from src.bounded_context.project_management.repos.project_repo import ProjectRepo


class RepoCollection:
    def __init__(
        self,
        environments_path: Path,
    ) -> None:
        self.project_repo = ProjectRepo(environments_path)
        self.session_manager = AgentSessionManager()
