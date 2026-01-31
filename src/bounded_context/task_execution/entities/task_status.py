from enum import Enum


class TaskStatus(Enum):
    NEW = "new"
    READY = "ready"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    IN_REVIEW = "in_review"
    DONE = "done"
    CLOSED = "closed"
