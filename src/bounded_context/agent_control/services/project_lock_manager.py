from redis import Redis


class ProjectLockManager:
    LOCK_PREFIX = "agent_fleet:lock:"

    def __init__(self, redis_url: str) -> None:
        self._redis = Redis.from_url(redis_url)

    def _lock_key(self, project_id: str) -> str:
        return f"{self.LOCK_PREFIX}{project_id}"

    def acquire_lock(self, project_id: str, ttl_seconds: int = 3600) -> bool:
        key = self._lock_key(project_id)
        result = self._redis.set(key, "locked", nx=True, ex=ttl_seconds)
        return result is True

    def release_lock(self, project_id: str) -> None:
        key = self._lock_key(project_id)
        self._redis.delete(key)

    def is_locked(self, project_id: str) -> bool:
        key = self._lock_key(project_id)
        result = self._redis.exists(key)
        return bool(result)

    def extend_lock(self, project_id: str, ttl_seconds: int) -> bool:
        key = self._lock_key(project_id)
        return bool(self._redis.expire(key, ttl_seconds))
