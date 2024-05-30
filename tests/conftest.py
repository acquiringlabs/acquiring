import os
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from types import TracebackType
from typing import Callable, Generator, Optional, Self
from unittest import mock
import pytest

from acquiring import domain, enums, protocols
from tests import protocols as test_protocols


# https://docs.pytest.org/en/7.1.x/reference/reference.html?highlight=pytest_config#pytest.hookspec.pytest_configure
def pytest_configure(config: Callable) -> None:
    try:
        import django
        from django.conf import settings

        from acquiring import settings as project_settings

        settings.configure(
            DATABASES=project_settings.DATABASES,
            INSTALLED_APPS=project_settings.INSTALLED_APPS,
            MIGRATION_MODULES=project_settings.MIGRATION_MODULES,
        )

        django.setup()
    except ImportError:
        # django isn't installed, skip
        return


@pytest.fixture()
def fake_os_environ() -> Generator:
    with mock.patch.dict(
        os.environ,
        {
            "PAYPAL_CLIENT_ID": "long-client-id",
            "PAYPAL_CLIENT_SECRET": "long-client-secret",
            "PAYPAL_BASE_URL": "https://api-m.sandbox.paypal.com/",
            "SQLALCHEMY_DATABASE_URL": "sqlite:///./db.sqlite3",
        },
    ):
        yield


@pytest.fixture()
def fake_payment_method_repository_class() -> (
    Callable[[Optional[list[protocols.PaymentMethod]]], type[protocols.Repository]]
):

    def func(payment_methods: Optional[list[protocols.PaymentMethod]]) -> type[protocols.Repository]:

        class FakePaymentMethodRepository:

            def __init__(self) -> None:
                """
                Cloning the list into units attribute to simulate the independence of database versus objects in memory
                """
                self.units = payment_methods.copy() if payment_methods is not None else []

            def add(self, data: protocols.DraftPaymentMethod) -> protocols.PaymentMethod:
                payment_method_id = uuid.uuid4()
                payment_method = domain.PaymentMethod(
                    id=payment_method_id,
                    created_at=datetime.now(),
                    payment_attempt=data.payment_attempt,
                    confirmable=data.confirmable,
                    tokens=[
                        domain.Token(
                            timestamp=token.timestamp,
                            token=token.token,
                            payment_method_id=payment_method_id,
                            metadata=token.metadata,
                            expires_at=token.expires_at,
                            fingerprint=token.fingerprint,
                        )
                        for token in data.tokens
                    ],
                    payment_operations=[],
                )
                self.units.append(payment_method)
                return payment_method

            def get(self, id: uuid.UUID) -> protocols.PaymentMethod:
                for unit in self.units:
                    if unit.id == id:
                        return unit
                raise domain.PaymentMethod.DoesNotExist

        return FakePaymentMethodRepository

    return func


@pytest.fixture
def fake_payment_operation_repository_class() -> (
    Callable[[Optional[set[protocols.PaymentOperation]]], type[test_protocols.FakeRepository]]
):

    def func(payment_operations: Optional[set[protocols.PaymentOperation]]) -> type[test_protocols.FakeRepository]:

        @dataclass
        class FakePaymentOperationRepository:
            def __init__(self) -> None:
                """
                Cloning the list into units attribute to simulate the independence of database versus objects in memory
                """
                self.units = payment_operations.copy() if payment_operations is not None else set()

            def add(
                self,
                payment_method: protocols.PaymentMethod,
                type: enums.OperationTypeEnum,
                status: enums.OperationStatusEnum,
            ) -> protocols.PaymentOperation:
                payment_operation = domain.PaymentOperation(
                    created_at=datetime.now(),
                    type=type,
                    status=status,
                    payment_method_id=payment_method.id,
                )
                payment_method.payment_operations.append(payment_operation)
                self.units.add(payment_operation)
                return payment_operation

            def get(  # type:ignore[empty-body]
                self, id: uuid.UUID
            ) -> protocols.PaymentOperation: ...

        return FakePaymentOperationRepository

    return func


@pytest.fixture(scope="module")
def fake_transaction_repository_class() -> (
    Callable[[Optional[set[protocols.Transaction]]], type[test_protocols.FakeRepository]]
):

    def func(transactions: Optional[set[protocols.Transaction]]) -> type[test_protocols.FakeRepository]:

        @dataclass
        class FakeTransactionRepository:
            def __init__(self) -> None:
                """
                Cloning the list into units attribute to simulate the independence of database versus objects in memory
                """
                self.units = transactions.copy() if transactions is not None else set()

            def add(self, transaction: protocols.Transaction) -> protocols.Transaction:
                transaction = domain.Transaction(
                    external_id=transaction.external_id,
                    timestamp=transaction.timestamp,
                    raw_data=transaction.raw_data,
                    provider_name=transaction.provider_name,
                    payment_method_id=transaction.payment_method_id,
                )
                self.units.add(transaction)
                return transaction

            def get(  # type:ignore[empty-body]
                self,
                id: uuid.UUID,
            ) -> protocols.Transaction: ...

        return FakeTransactionRepository

    return func


@pytest.fixture(scope="module")
def fake_block_event_repository_class() -> (
    Callable[[Optional[set[protocols.BlockEvent]]], type[test_protocols.FakeRepository]]
):

    def func(block_events: Optional[set[protocols.BlockEvent]]) -> type[test_protocols.FakeRepository]:

        @dataclass
        class FakeBlockEventRepository:

            def __init__(self) -> None:
                """
                Cloning the list into units attribute to simulate the independence of database versus objects in memory
                """
                self.units = block_events.copy() if block_events is not None else set()

            def add(self, block_event: protocols.BlockEvent) -> protocols.BlockEvent:
                block_event = domain.BlockEvent(
                    created_at=datetime.now(),
                    status=block_event.status,
                    payment_method_id=block_event.payment_method_id,
                    block_name=block_event.block_name,
                )
                self.units.add(block_event)
                return block_event

            def get(  # type:ignore[empty-body]
                self, id: uuid.UUID
            ) -> protocols.BlockEvent: ...

        return FakeBlockEventRepository

    return func


@pytest.fixture(scope="module")
def fake_unit_of_work() -> type[test_protocols.FakeUnitOfWork]:

    @dataclass
    class FakeUnitOfWork:
        payment_method_repository_class: type[protocols.Repository]
        payment_methods: protocols.Repository = field(init=False, repr=False)

        payment_operation_repository_class: type[test_protocols.FakeRepository]
        payment_operations: test_protocols.FakeRepository = field(init=False, repr=False)

        block_event_repository_class: type[test_protocols.FakeRepository]
        block_events: test_protocols.FakeRepository = field(init=False, repr=False)

        transaction_repository_class: type[test_protocols.FakeRepository]
        transactions: test_protocols.FakeRepository = field(init=False, repr=False)

        payment_method_units: list[protocols.PaymentMethod] = field(default_factory=list)
        payment_operation_units: set[protocols.PaymentOperation] = field(default_factory=set)
        block_event_units: set[protocols.BlockEvent] = field(default_factory=set)

        transaction_units: set[protocols.Transaction] = field(default_factory=set)

        def __enter__(self) -> Self:
            self.payment_methods = self.payment_method_repository_class()
            self.payment_method_units = self.payment_methods.units  # type:ignore[attr-defined]

            self.payment_operations = self.payment_operation_repository_class()
            self.payment_operation_units.update(unit for unit in self.payment_operations.units)

            self.block_events = self.block_event_repository_class()
            self.block_event_units.update(unit for unit in self.block_events.units)

            self.transactions = self.transaction_repository_class()
            self.transaction_units.update(unit for unit in self.transactions.units)
            return self

        def __exit__(
            self,
            exc_type: Optional[type[Exception]],
            exc_value: Optional[type[Exception]],
            exc_tb: Optional[TracebackType],
        ) -> None:
            pass

        def commit(self) -> None:
            """Refreshes the units with those inside the repository"""
            self.payment_method_units = self.payment_methods.units  # type:ignore[attr-defined]

            self.payment_operation_units.update(unit for unit in self.payment_operations.units)

            self.block_event_units.update(unit for unit in self.block_events.units)

            self.transaction_units.update(unit for unit in self.transactions.units)

        def rollback(self) -> None:
            pass

    return FakeUnitOfWork
