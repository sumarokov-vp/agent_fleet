import redis
from bot_framework.entities.bot_message import BotMessage


class RedisMessageForReplaceStorage:
    KEY_PREFIX = "agent_fleet:message_for_replace:"
    TTL_SECONDS = 86400

    def __init__(self, redis_url: str) -> None:
        self._redis = redis.from_url(redis_url)  # pyright: ignore[reportUnknownMemberType]

    def _get_key(self, user_id: int) -> str:
        return f"{self.KEY_PREFIX}{user_id}"

    def save(self, user_id: int, message: BotMessage) -> None:
        key = self._get_key(user_id)
        self._redis.set(key, message.model_dump_json(), ex=self.TTL_SECONDS)

    def get(self, user_id: int) -> BotMessage | None:
        key = self._get_key(user_id)
        data = self._redis.get(key)
        if not data:
            return None
        return BotMessage.model_validate_json(data)  # pyright: ignore[reportArgumentType]

    def clear(self, user_id: int) -> None:
        key = self._get_key(user_id)
        self._redis.delete(key)
