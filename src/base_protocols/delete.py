from typing import Protocol, TypeVar

T = TypeVar("T", contravariant=True)


class DeleteProtocol(Protocol[T]):
    def delete(self, entity: T) -> None: ...
