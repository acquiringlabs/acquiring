from dataclasses import dataclass
from types import TracebackType
from typing import Self

import django.db.transaction


@dataclass
class DjangoUnitOfWork:
    """
    Despite Cosmic Python's suggestion, a better approach is to delegate
    to transaction.atomic instead of setting autocommit to False, then revert to True.

    I trust that this code is better than anything I could build myself.
    """

    def __enter__(self) -> Self:
        """
        See django.db.transaction Atomic.__enter__ here
        https://github.com/django/django/blob/main/django/db/transaction.py#L182
        """
        self.transaction = django.db.transaction.atomic()
        self.transaction.__enter__()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """
        See django.db.transaction Atomic.__exit__ here
        https://github.com/django/django/blob/main/django/db/transaction.py#L224
        """
        return self.transaction.__exit__(exc_type, exc_value, exc_tb)

    def commit(self) -> None:
        """
        In Django, savepoints can be implemented by exiting the transaction and initiating a new one.
        """
        self.transaction.__exit__(None, None, None)
        self.__enter__()

    def rollback(self) -> None:
        django.db.transaction.set_rollback(True)
