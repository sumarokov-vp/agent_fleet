import os
from pathlib import Path

from bot_framework.app.bot_application import BotApplication
from dotenv import load_dotenv

from workers.bot.repo_collection import RepoCollection


def main() -> None:
    load_dotenv()

    bot_token = os.environ["TELEGRAM_BOT_TOKEN"]
    database_url = os.environ["DB_URL"]
    redis_url = os.environ["REDIS_URL"]

    environments_path = Path(__file__).parent.parent.parent / "environments.yaml"
    data_path = Path(__file__).parent.parent.parent / "data"

    repos = RepoCollection(
        environments_path=environments_path,
        redis_url=redis_url,
    )

    app = BotApplication(
        bot_token=bot_token,
        database_url=database_url,
        redis_url=redis_url,
        phrases_json_path=data_path / "phrases.json",
        languages_json_path=data_path / "languages.json",
        roles_json_path=data_path / "roles.json",
    )

    # TODO: register flows when implemented
    _ = repos  # Will be used for flow registration

    app.run()


if __name__ == "__main__":
    main()
