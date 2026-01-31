from typing import Protocol, TypeVar

T = TypeVar("T")


class GetAllProtocol(Protocol[T]):
    def get_all(self) -> list[T]: ...
