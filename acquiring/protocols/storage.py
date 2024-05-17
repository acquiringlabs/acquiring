from dataclasses import dataclass, field
from types import TracebackType
from typing import Optional, Protocol, Self, runtime_checkable
from uuid import UUID


@runtime_checkable
class Repository(Protocol):

    def add(self, *args, **kwargs): ...  # type:ignore[no-untyped-def]

    def get(self, id: UUID): ...  # type: ignore[no-untyped-def]


@dataclass(match_args=False)
class UnitOfWork(Protocol):
    payment_method_repository_class: type[Repository]
    payment_methods: Repository = field(init=False)

    payment_operation_repository_class: type[Repository]
    payment_operations: Repository = field(init=False)

    block_event_repository_class: type[Repository]
    block_events: Repository = field(init=False)

    transaction_repository_class: type[Repository]
    transactions: Repository = field(init=False)

    def __enter__(self) -> Self: ...

    def __exit__(
        self,
        exc_type: Optional[type[Exception]],
        exc_value: Optional[type[Exception]],
        exc_tb: Optional[TracebackType],
    ) -> None: ...

    def commit(self) -> None:
        """
        Commit any pending transaction to the database.

        Note that if the database supports an auto-commit feature, this must be initially off.
        An interface method may be provided to turn it back on.

        Database modules that do not support transactions should implement this method with void functionality.

        See https://peps.python.org/pep-0249/#commit
        """
        pass

    def rollback(self) -> None:
        """
        This method is optional since not all databases provide transaction support.
        If the database does not support the functionality required by the method,
        the interface should throw an exception in case the method is used.

        In case a database does provide transactions this method causes the database to roll back
        to the start of any pending transaction.

        Closing a connection without committing the changes first will cause an implicit rollback to be performed.

        See https://peps.python.org/pep-0249/#rollback
        """
        pass
