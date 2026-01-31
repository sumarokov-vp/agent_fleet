import json

import redis


class RedisPendingPromptStorage:
    KEY_PREFIX = "agent_fleet:pending_prompt:"
    TTL_SECONDS = 300

    def __init__(self, redis_url: str) -> None:
        self._redis = redis.from_url(redis_url)  # pyright: ignore[reportUnknownMemberType]

    def _get_key(self, user_id: int) -> str:
        return f"{self.KEY_PREFIX}{user_id}"

    def save_pending_prompt(
        self, user_id: int, project_id: str, prompt: str
    ) -> None:
        key = self._get_key(user_id)
        data = json.dumps({"project_id": project_id, "prompt": prompt})
        self._redis.set(key, data, ex=self.TTL_SECONDS)

    def get_pending_prompt(self, user_id: int) -> tuple[str, str] | None:
        key = self._get_key(user_id)
        data = self._redis.get(key)
        if not data:
            return None
        parsed = json.loads(str(data, "utf-8"))  # pyright: ignore[reportArgumentType]
        return (parsed["project_id"], parsed["prompt"])

    def clear_pending_prompt(self, user_id: int) -> None:
        key = self._get_key(user_id)
        self._redis.delete(key)
