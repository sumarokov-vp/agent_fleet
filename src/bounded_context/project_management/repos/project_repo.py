from pathlib import Path

import yaml

from src.bounded_context.project_management.entities.project import (
    Project,
    TaskSystemConfig,
)


class ProjectRepo:
    def __init__(self, config_path: Path) -> None:
        self._config_path = config_path
        self._projects: dict[str, Project] = {}
        self._load_projects()

    def _load_projects(self) -> None:
        with self._config_path.open() as f:
            data = yaml.safe_load(f)

        environments = data.get("environments", {})
        for project_id, config in environments.items():
            task_system = None
            if "task_system" in config:
                task_system = TaskSystemConfig(**config["task_system"])

            self._projects[project_id] = Project(
                id=project_id,
                description=config.get("description", ""),
                path=config.get("path", ""),
                task_system=task_system,
            )

    def get_all(self) -> list[Project]:
        return list(self._projects.values())

    def get_by_id(self, project_id: str) -> Project | None:
        return self._projects.get(project_id)

    def reload(self) -> None:
        self._projects.clear()
        self._load_projects()
