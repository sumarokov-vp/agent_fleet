from typing import Protocol, TypeVar

T = TypeVar("T", covariant=True)


class ReadProtocol(Protocol[T]):
    def get_by_id(self, id: int) -> T: ...

    def find_by_id(self, id: int) -> T | None: ...
