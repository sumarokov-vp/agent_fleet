from src.bounded_context.agent_control.services.agent_session_manager import (
    AgentSessionManager,
)
from src.bounded_context.project_management.entities.project import Project
from src.flows.ask_flow.presenters.execution_progress_presenter import (
    ExecutionProgressPresenter,
)


class PromptExecutor:
    def __init__(
        self,
        session_manager: AgentSessionManager,
        progress_presenter: ExecutionProgressPresenter,
    ) -> None:
        self._session_manager = session_manager
        self._progress_presenter = progress_presenter

    async def execute(
        self,
        project: Project,
        prompt: str,
        user_id: int,
        language_code: str,
    ) -> None:
        session = None
        try:
            self._progress_presenter.send_started(
                chat_id=user_id,
                language_code=language_code,
            )

            session = self._session_manager.create_session(
                project_id=project.id,
                working_directory=project.path,
            )

            client = self._session_manager.get_client(session.id)
            if not client:
                return

            await client.connect()
            await client.query(prompt)
            async for message in client.receive_messages():
                self._progress_presenter.send_message(
                    chat_id=user_id,
                    message=message,
                )

            self._progress_presenter.send_completed(
                chat_id=user_id,
                language_code=language_code,
            )
        finally:
            if session:
                await self._session_manager.close_session(session.id)
