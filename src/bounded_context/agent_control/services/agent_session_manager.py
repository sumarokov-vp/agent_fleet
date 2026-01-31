import uuid
from datetime import UTC, datetime
from typing import Literal

from claude_code_sdk import ClaudeCodeOptions, ClaudeSDKClient

from src.bounded_context.task_execution.entities.execution_session import (
    ExecutionSession,
    SessionStatus,
)

PermissionModeType = Literal["default", "acceptEdits", "plan"]


class AgentSessionManager:
    def __init__(self) -> None:
        self._sessions: dict[str, ExecutionSession] = {}
        self._clients: dict[str, ClaudeSDKClient] = {}

    def create_session(
        self,
        project_id: str,
        working_directory: str,
        task_id: str | None = None,
        permission_mode: PermissionModeType = "default",
        resume_session_id: str | None = None,
    ) -> ExecutionSession:
        session_id = str(uuid.uuid4())
        sdk_permission_mode = self._map_permission_mode(permission_mode)
        options = ClaudeCodeOptions(
            cwd=working_directory,
            permission_mode=sdk_permission_mode,
            resume=resume_session_id,
        )
        client = ClaudeSDKClient(options=options)

        session = ExecutionSession(
            id=session_id,
            project_id=project_id,
            task_id=task_id,
            working_directory=working_directory,
            status=SessionStatus.ACTIVE,
        )

        self._sessions[session_id] = session
        self._clients[session_id] = client
        return session

    def get_session(self, session_id: str) -> ExecutionSession | None:
        return self._sessions.get(session_id)

    def get_client(self, session_id: str) -> ClaudeSDKClient | None:
        return self._clients.get(session_id)

    async def interrupt_session(self, session_id: str) -> bool:
        client = self._clients.get(session_id)
        session = self._sessions.get(session_id)
        if not client or not session:
            return False

        await client.interrupt()
        session.status = SessionStatus.INTERRUPTED
        return True

    async def close_session(self, session_id: str) -> None:
        client = self._clients.get(session_id)
        session = self._sessions.get(session_id)

        if client:
            await client.disconnect()
            del self._clients[session_id]

        if session:
            session.status = SessionStatus.COMPLETED
            session.ended_at = datetime.now(tz=UTC)

    def get_active_sessions(self) -> list[ExecutionSession]:
        return [s for s in self._sessions.values() if s.status == SessionStatus.ACTIVE]

    def get_session_by_project(self, project_id: str) -> ExecutionSession | None:
        for session in self._sessions.values():
            if session.project_id == project_id and session.status == SessionStatus.ACTIVE:
                return session
        return None

    def _map_permission_mode(self, mode: PermissionModeType) -> PermissionModeType:
        return mode
