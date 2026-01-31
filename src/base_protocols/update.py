from typing import Protocol, TypeVar

T = TypeVar("T")


class UpdateProtocol(Protocol[T]):
    def update(self, entity: T) -> T: ...
