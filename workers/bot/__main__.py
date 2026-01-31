import logging
import os
from pathlib import Path

from bot_framework.app.bot_application import BotApplication
from dotenv import load_dotenv

from src.flows.ask_flow import AskFlowFactory, RedisPendingPromptStorage
from src.flows.execution_control_flow import ExecutionControlFlowFactory
from src.flows.project_selection_flow import ProjectSelectionFlowFactory
from src.flows.welcome_flow import WelcomeMenuSender
from src.shared import RedisMessageForReplaceStorage, RedisProjectSelectionStateStorage
from workers.bot.repo_collection import RepoCollection

logger = logging.getLogger(__name__)


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
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

    app.set_start_allowed_roles({"admin", "developer"})

    project_state_storage = RedisProjectSelectionStateStorage(redis_url)
    message_for_replace_storage = RedisMessageForReplaceStorage(redis_url)
    pending_prompt_storage = RedisPendingPromptStorage(redis_url)

    project_selection_factory = ProjectSelectionFlowFactory(
        callback_answerer=app.callback_answerer,
        message_service=app.message_service,
        phrase_repo=app.phrase_repo,
        project_repo=repos.project_repo,
        state_storage=project_state_storage,
        message_for_replace_storage=message_for_replace_storage,
        user_repo=app.user_repo,
    )
    project_selection_factory.register_handlers(
        callback_registry=app.callback_handler_registry,
    )

    execution_control_factory = ExecutionControlFlowFactory(
        callback_answerer=app.callback_answerer,
        message_service=app.message_service,
        phrase_repo=app.phrase_repo,
        user_repo=app.user_repo,
        project_repo=repos.project_repo,
        project_state_storage=project_state_storage,
        session_manager=repos.session_manager,
    )
    execution_control_factory.register_handlers(
        callback_registry=app.callback_handler_registry,
    )

    ask_flow_factory = AskFlowFactory(
        callback_answerer=app.callback_answerer,
        message_service=app.message_service,
        phrase_repo=app.phrase_repo,
        user_repo=app.user_repo,
        project_repo=repos.project_repo,
        project_state_storage=project_state_storage,
        pending_prompt_storage=pending_prompt_storage,
        message_for_replace_storage=message_for_replace_storage,
        lock_manager=repos.lock_manager,
        session_manager=repos.session_manager,
    )
    ask_flow_factory.register_handlers(
        callback_registry=app.callback_handler_registry,
    )

    app.add_main_menu_button(
        "menu.stop",
        execution_control_factory.get_stop_callback_handler(),
    )
    app.add_main_menu_button(
        "menu.status",
        execution_control_factory.get_status_callback_handler(),
    )
    app.add_main_menu_button(
        "menu.projects",
        project_selection_factory.get_project_list_callback_handler(),
    )

    welcome_menu_sender = WelcomeMenuSender(
        message_service=app.message_service,
        phrase_repo=app.phrase_repo,
        project_repo=repos.project_repo,
        state_storage=project_state_storage,
        message_for_replace_storage=message_for_replace_storage,
        buttons=app._main_menu_sender.buttons,
    )
    app._start_command_handler.main_menu_sender = welcome_menu_sender

    app.core.message_handler_registry.register(
        handler=ask_flow_factory.create_text_message_handler(),
        content_types=["text"],
    )

    logger.info("Bot started")
    app.run()


if __name__ == "__main__":
    main()
