from typing import Protocol, TypeVar

T = TypeVar("T")


class CreateProtocol(Protocol[T]):
    def create(self, entity: T) -> T: ...
