import redis


class RedisProjectSelectionStateStorage:
    KEY_PREFIX = "agent_fleet:selected_project:"
    TTL_SECONDS = 86400

    def __init__(self, redis_url: str) -> None:
        self._redis = redis.from_url(redis_url)  # pyright: ignore[reportUnknownMemberType]

    def _get_key(self, user_id: int) -> str:
        return f"{self.KEY_PREFIX}{user_id}"

    def save_selected_project(self, user_id: int, project_id: str) -> None:
        key = self._get_key(user_id)
        self._redis.set(key, project_id, ex=self.TTL_SECONDS)

    def get_selected_project(self, user_id: int) -> str | None:
        key = self._get_key(user_id)
        data = self._redis.get(key)
        if not data:
            return None
        return str(data, "utf-8")  # pyright: ignore[reportArgumentType]

    def clear_selection(self, user_id: int) -> None:
        key = self._get_key(user_id)
        self._redis.delete(key)
