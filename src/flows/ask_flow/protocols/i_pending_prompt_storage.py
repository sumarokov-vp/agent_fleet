from typing import Protocol


class IPendingPromptStorage(Protocol):
    def save_pending_prompt(
        self, user_id: int, project_id: str, prompt: str
    ) -> None: ...

    def get_pending_prompt(self, user_id: int) -> tuple[str, str] | None: ...

    def clear_pending_prompt(self, user_id: int) -> None: ...
