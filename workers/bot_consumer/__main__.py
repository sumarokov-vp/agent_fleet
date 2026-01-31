import asyncio
import logging
import os

from bot_framework.language_management.providers.redis_phrase_provider import (
    RedisPhraseProvider,
)
from bot_framework.telegram.services.telegram_message_core import TelegramMessageCore
from bot_framework.telegram.services.telegram_message_service import TelegramMessageService
from dotenv import load_dotenv

from src.flows.ask_flow.presenters.ask_user_question_presenter import (
    AskUserQuestionPresenter,
)
from src.flows.ask_flow.presenters.execution_progress_presenter import (
    ExecutionProgressPresenter,
)
from src.flows.ask_flow.presenters.plan_ready_presenter import PlanReadyPresenter
from src.messaging import RabbitMQConnection
from src.shared import RedisMessageForReplaceStorage
from workers.bot.consumers.claude_response_consumer import ClaudeResponseConsumer

logger = logging.getLogger(__name__)


async def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    load_dotenv()

    bot_token = os.environ["BOT_TOKEN"]
    redis_url = os.environ["REDIS_URL"]
    rabbitmq_url = os.environ["RABBITMQ_URL"]

    core = TelegramMessageCore(bot_token=bot_token, use_class_middlewares=False)
    message_service = TelegramMessageService(core)
    phrase_repo = RedisPhraseProvider(redis_url)
    message_for_replace_storage = RedisMessageForReplaceStorage(redis_url)

    progress_presenter = ExecutionProgressPresenter(
        message_service=message_service,
        phrase_repo=phrase_repo,
        message_for_replace_storage=message_for_replace_storage,
    )
    ask_question_presenter = AskUserQuestionPresenter(
        message_service=message_service,
        phrase_repo=phrase_repo,
    )
    plan_ready_presenter = PlanReadyPresenter(
        message_service=message_service,
        phrase_repo=phrase_repo,
    )

    connection = RabbitMQConnection(rabbitmq_url)
    await connection.connect()

    consumer = ClaudeResponseConsumer(
        connection=connection,
        progress_presenter=progress_presenter,
        ask_question_presenter=ask_question_presenter,
        plan_ready_presenter=plan_ready_presenter,
    )

    await consumer.start()

    logger.info("Bot consumer started, waiting for responses...")
    await asyncio.Event().wait()


if __name__ == "__main__":
    asyncio.run(main())
