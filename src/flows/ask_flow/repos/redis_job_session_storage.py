from uuid import UUID

import redis


class RedisJobSessionStorage:
    KEY_PREFIX = "agent_fleet:job_session:"
    TTL_SECONDS = 3600

    def __init__(self, redis_url: str) -> None:
        self._redis = redis.from_url(redis_url)  # pyright: ignore[reportUnknownMemberType]

    def _get_key(self, session_id: str) -> str:
        return f"{self.KEY_PREFIX}{session_id}"

    def save_job_id(self, session_id: str, job_id: UUID) -> None:
        key = self._get_key(session_id)
        self._redis.set(key, str(job_id), ex=self.TTL_SECONDS)

    def get_job_id(self, session_id: str) -> UUID | None:
        key = self._get_key(session_id)
        value = self._redis.get(key)
        if value:
            decoded = value.decode("utf-8")  # pyright: ignore[reportAttributeAccessIssue]
            return UUID(decoded)
        return None
