from dataclasses import dataclass, field
from types import TracebackType
from typing import Self

import django.db.transaction

from acquiring import protocols


@dataclass
class DjangoUnitOfWork:
    """
    Unit of Work context manager for Django.

    See Unit of Work pattern here: https://martinfowler.com/eaaCatalog/unitOfWork.html
    """

    payment_method_repository_class: type[protocols.Repository]
    payment_methods: protocols.Repository = field(init=False, repr=False)

    payment_operation_repository_class: type[protocols.Repository]
    payment_operations: protocols.Repository = field(init=False, repr=False)

    block_event_repository_class: type[protocols.Repository]
    block_events: protocols.Repository = field(init=False, repr=False)

    transaction_repository_class: type[protocols.Repository]
    transactions: protocols.Repository = field(init=False, repr=False)

    def __enter__(self) -> Self:
        """
        Despite Cosmic Python's suggestion, a better approach is to delegate
        to transaction.atomic instead of setting autocommit to False, then revert to True.

        See django.db.transaction Atomic.__enter__ here
        https://github.com/django/django/blob/main/django/db/transaction.py#L182

        I trust that that code is better than anything I could build myself.
        """
        self.transaction = django.db.transaction.atomic()
        self.transaction.__enter__()
        self.payment_methods = self.payment_method_repository_class()
        self.payment_operations = self.payment_operation_repository_class()
        self.block_events = self.block_event_repository_class()
        self.transactions = self.transaction_repository_class()

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
