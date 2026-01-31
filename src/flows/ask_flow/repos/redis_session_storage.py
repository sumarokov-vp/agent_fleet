import redis


class RedisSessionStorage:
    KEY_PREFIX = "agent_fleet:claude_session:"
    TTL_SECONDS = 3600

    def __init__(self, redis_url: str) -> None:
        self._redis = redis.from_url(redis_url)  # pyright: ignore[reportUnknownMemberType]

    def _get_key(self, user_id: int) -> str:
        return f"{self.KEY_PREFIX}{user_id}"

    def save_session_id(self, user_id: int, session_id: str) -> None:
        key = self._get_key(user_id)
        self._redis.set(key, session_id, ex=self.TTL_SECONDS)

    def get_session_id(self, user_id: int) -> str | None:
        key = self._get_key(user_id)
        value = self._redis.get(key)
        if value:
            return value.decode("utf-8")  # pyright: ignore[reportAttributeAccessIssue]
        return None

    def clear_session_id(self, user_id: int) -> None:
        key = self._get_key(user_id)
        self._redis.delete(key)
