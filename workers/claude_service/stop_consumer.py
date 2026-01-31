import logging

from src.bounded_context.agent_control.services.agent_session_manager import (
    AgentSessionManager,
)
from src.messaging import MessageConsumer, StopRequest
from src.messaging.connection import RabbitMQConnection

logger = logging.getLogger(__name__)


class StopRequestConsumer(MessageConsumer[StopRequest]):
    def __init__(
        self,
        connection: RabbitMQConnection,
        session_manager: AgentSessionManager,
    ) -> None:
        super().__init__(
            connection=connection,
            exchange_name="claude.requests",
            queue_name="claude.stop",
            routing_key="claude.stop",
            prefetch_count=5,
        )
        self._session_manager = session_manager

    def _parse_message(self, body: bytes) -> StopRequest:
        return StopRequest.model_validate_json(body)

    async def _handle_message(self, message: StopRequest) -> None:
        logger.info(
            "Processing stop request for user %s (project: %s)",
            message.user_id,
            message.project_id,
        )

        session = self._session_manager.get_session_by_project(message.project_id)
        if session:
            await self._session_manager.interrupt_session(session.id)
            logger.info("Session %s interrupted", session.id)
        else:
            logger.info("No active session found for project %s", message.project_id)
