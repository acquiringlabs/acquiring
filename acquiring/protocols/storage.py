from typing import Protocol, runtime_checkable
from uuid import UUID


@runtime_checkable
class Repository(Protocol):

    def add(self, *args, **kwargs): ...  # type:ignore[no-untyped-def]

    def get(self, id: UUID): ...  # type: ignore[no-untyped-def]


class UnitOfWork(Protocol):

    def __enter__(self): ...  # type:ignore[no-untyped-def]

    def __exit__(self, exc_type, exc_value, exc_tb): ...  # type:ignore[no-untyped-def]

    def commit(self): ...  # type:ignore[no-untyped-def]

    def rollback(self): ...  # type:ignore[no-untyped-def]
