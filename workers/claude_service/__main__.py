import asyncio
import logging
import os

from dotenv import load_dotenv

from src.bounded_context.agent_control.services.agent_session_manager import (
    AgentSessionManager,
)
from src.bounded_context.claude_service.migrations.runner import apply_migrations
from src.bounded_context.claude_service.repos.job_repo import JobRepo
from src.bounded_context.claude_service.repos.session_repo import SessionRepo
from src.messaging import MessagePublisher, RabbitMQConnection
from workers.claude_service.request_consumer import ClaudeRequestConsumer
from workers.claude_service.stop_consumer import StopRequestConsumer

logger = logging.getLogger(__name__)


async def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    load_dotenv()

    redis_url = os.environ["REDIS_URL"]
    rabbitmq_url = os.environ["RABBITMQ_URL"]
    claude_service_db_url = os.environ["CLAUDE_SERVICE_DB_URL"]

    logger.info("Applying database migrations...")
    apply_migrations(claude_service_db_url)
    logger.info("Database migrations applied")

    job_repo = JobRepo(claude_service_db_url)
    session_repo = SessionRepo(claude_service_db_url)

    connection = RabbitMQConnection(rabbitmq_url)
    await connection.connect()

    response_publisher = MessagePublisher(connection, "claude.responses")
    session_manager = AgentSessionManager()

    request_consumer = ClaudeRequestConsumer(
        connection=connection,
        session_manager=session_manager,
        response_publisher=response_publisher,
        job_repo=job_repo,
        session_repo=session_repo,
        redis_url=redis_url,
    )

    stop_consumer = StopRequestConsumer(
        connection=connection,
        session_manager=session_manager,
    )

    await request_consumer.start()
    await stop_consumer.start()

    logger.info("Claude Service started, waiting for requests...")
    await asyncio.Event().wait()


if __name__ == "__main__":
    asyncio.run(main())
