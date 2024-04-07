from typing import Protocol, runtime_checkable
from uuid import UUID


@runtime_checkable
class AbstractRepository(Protocol):

    def add(self, *args, **kwargs): ...  # type:ignore[no-untyped-def]

    def get(self, id: UUID): ...  # type: ignore[no-untyped-def]
