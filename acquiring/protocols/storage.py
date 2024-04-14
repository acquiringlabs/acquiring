from types import TracebackType
from typing import Optional, Protocol, Self, runtime_checkable
from uuid import UUID


@runtime_checkable
class Repository(Protocol):

    def add(self, *args, **kwargs): ...  # type:ignore[no-untyped-def]

    def get(self, id: UUID): ...  # type: ignore[no-untyped-def]


class UnitOfWork(Protocol):

    def __enter__(self) -> Self: ...

    def __exit__(
        self,
        exc_type: Optional[type[Exception]],
        exc_value: Optional[type[Exception]],
        exc_tb: Optional[TracebackType],
    ) -> None: ...

    def commit(self) -> None: ...

    def rollback(self) -> None: ...
