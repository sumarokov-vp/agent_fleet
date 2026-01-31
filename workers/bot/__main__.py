import os
from pathlib import Path

from bot_framework.app.bot_application import BotApplication
from dotenv import load_dotenv

from src.flows.ask_flow import AskFlowFactory
from src.flows.execution_control_flow import ExecutionControlFlowFactory
from src.flows.project_selection_flow import (
    ProjectSelectionFlowFactory,
    RedisProjectSelectionStateStorage,
)
from workers.bot.repo_collection import RepoCollection


def main() -> None:
    load_dotenv()

    bot_token = os.environ["BOT_TOKEN"]
    bot_database_url = os.environ["BOT_DB_URL"]
    redis_url = os.environ["REDIS_URL"]

    environments_path = Path(__file__).parent.parent.parent / "environments.yaml"
    data_path = Path(__file__).parent.parent.parent / "data"

    repos = RepoCollection(
        environments_path=environments_path,
        redis_url=redis_url,
    )

    app = BotApplication(
        bot_token=bot_token,
        database_url=bot_database_url,
        redis_url=redis_url,
        phrases_json_path=data_path / "phrases.json",
        languages_json_path=data_path / "languages.json",
        roles_json_path=data_path / "roles.json",
    )

    project_state_storage = RedisProjectSelectionStateStorage(redis_url)

    project_selection_factory = ProjectSelectionFlowFactory(
        callback_answerer=app.callback_answerer,
        message_sender=app.message_sender,
        phrase_repo=app.phrase_repo,
        project_repo=repos.project_repo,
        state_storage=project_state_storage,
        user_repo=app.user_repo,
    )
    project_selection_factory.register_handlers(
        callback_registry=app.callback_handler_registry,
        message_registry=app.core.message_handler_registry,
    )

    ask_flow_factory = AskFlowFactory(
        message_sender=app.message_sender,
        phrase_repo=app.phrase_repo,
        user_repo=app.user_repo,
        project_repo=repos.project_repo,
        project_state_storage=project_state_storage,
        lock_manager=repos.lock_manager,
        session_manager=repos.session_manager,
    )
    ask_flow_factory.register_handlers(
        message_registry=app.core.message_handler_registry,
    )

    execution_control_factory = ExecutionControlFlowFactory(
        message_sender=app.message_sender,
        phrase_repo=app.phrase_repo,
        user_repo=app.user_repo,
        project_repo=repos.project_repo,
        project_state_storage=project_state_storage,
        session_manager=repos.session_manager,
    )
    execution_control_factory.register_handlers(
        message_registry=app.core.message_handler_registry,
    )

    app.run()


if __name__ == "__main__":
    main()
