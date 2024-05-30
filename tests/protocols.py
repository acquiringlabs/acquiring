from dataclasses import dataclass, field
from typing import Generic, Protocol, TypeVar

from acquiring import protocols

Unit = TypeVar("Unit", bound=type)


class FakeRepository(Generic[Unit], protocols.Repository, Protocol):
    """
    In order to test the functionality of Repositories,
    the testing interface includes an extra parameter called units,
    meant to be accessed in lieu of a database call.

    Otherwise it is meant to be the same interface as a normal Repository,
    therefore it inherits from that protocol.
    """

    units: set[Unit]


@dataclass(match_args=False)
class FakeUnitOfWork(protocols.UnitOfWork, Protocol):
    """
    Combines the interface of protocols.UnitOfWork
    with the ability to introspect what's on the database for testing purposes via units
    """

    """
    Payment methods cannot be associated with a FakeRepository
    since they are mutable by definition (contain payment_operations)
    """
    payment_method_repository_class: type[protocols.Repository]
    payment_methods: protocols.Repository = field(init=False, repr=False)

    payment_operation_repository_class: type[FakeRepository]
    payment_operations: FakeRepository = field(init=False, repr=False)

    block_event_repository_class: type[FakeRepository]
    block_events: FakeRepository = field(init=False, repr=False)

    transaction_repository_class: type[FakeRepository]
    transactions: FakeRepository = field(init=False, repr=False)

    payment_method_units: list[protocols.PaymentMethod] = field(init=False, repr=False)
    payment_operation_units: set[protocols.PaymentOperation] = field(init=False, repr=False)
    block_event_units: set[protocols.BlockEvent] = field(init=False, repr=False)

    transaction_units: set[protocols.Transaction] = field(init=False, repr=False)
