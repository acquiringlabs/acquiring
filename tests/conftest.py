import os
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from types import TracebackType
from typing import Callable, Generator, List, Optional, Self
from unittest import mock

import pytest

from acquiring import domain, enums, protocols


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
                self.units = payment_methods or []

            def add(self, data: protocols.DraftPaymentMethod) -> protocols.PaymentMethod:
                payment_method_id = uuid.uuid4()
                payment_method = domain.PaymentMethod(
                    id=payment_method_id,
                    created_at=datetime.now(),
                    payment_attempt=data.payment_attempt,
                    confirmable=data.confirmable,
                    tokens=[
                        domain.Token(
                            created_at=token.created_at,
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
    Callable[[Optional[list[protocols.PaymentOperation]]], type[protocols.Repository]]
):

    def func(payment_operations: Optional[list[protocols.PaymentOperation]]) -> type[protocols.Repository]:

        @dataclass
        class FakePaymentOperationRepository:
            def __init__(self) -> None:
                self.units = payment_operations or []

            def add(
                self,
                payment_method: protocols.PaymentMethod,
                type: enums.OperationTypeEnum,
                status: enums.OperationStatusEnum,
            ) -> protocols.PaymentOperation:
                payment_operation = domain.PaymentOperation(
                    type=type,
                    status=status,
                    payment_method_id=payment_method.id,
                )
                payment_method.payment_operations.append(payment_operation)
                return payment_operation

            def get(  # type:ignore[empty-body]
                self, id: uuid.UUID
            ) -> protocols.PaymentOperation: ...

        return FakePaymentOperationRepository

    return func


@pytest.fixture(scope="module")
def fake_transaction_repository() -> Callable[
    [Optional[List[protocols.Transaction]]],
    protocols.Repository,
]:

    @dataclass
    class FakeTransactionRepository:
        units: List[protocols.Transaction]

        def add(self, transaction: protocols.Transaction) -> protocols.Transaction:
            transaction = domain.Transaction(
                external_id=transaction.external_id,
                timestamp=transaction.timestamp,
                raw_data=transaction.raw_data,
                provider_name=transaction.provider_name,
                payment_method_id=transaction.payment_method_id,
            )
            self.units.append(transaction)
            return transaction

        def get(  # type:ignore[empty-body]
            self,
            id: uuid.UUID,
        ) -> protocols.Transaction: ...

    def build_repository(
        units: Optional[list[protocols.Transaction]] = None,
    ) -> protocols.Repository:
        return FakeTransactionRepository(units=units if units else [])

    return build_repository


@pytest.fixture(scope="module")
def fake_transaction_repository_class() -> (
    Callable[[Optional[list[protocols.Transaction]]], type[protocols.Repository]]
):

    def func(transactions: Optional[list[protocols.Transaction]]) -> type[protocols.Repository]:

        @dataclass
        class FakeTransactionRepository:
            def __init__(self) -> None:
                self.units = transactions or []

            def add(self, transaction: protocols.Transaction) -> protocols.Transaction:
                transaction = domain.Transaction(
                    external_id=transaction.external_id,
                    timestamp=transaction.timestamp,
                    raw_data=transaction.raw_data,
                    provider_name=transaction.provider_name,
                    payment_method_id=transaction.payment_method_id,
                )
                self.units.append(transaction)
                return transaction

            def get(  # type:ignore[empty-body]
                self,
                id: uuid.UUID,
            ) -> protocols.Transaction: ...

        return FakeTransactionRepository

    return func


@pytest.fixture(scope="module")
def fake_block_event_repository_class() -> Callable[[Optional[list[protocols.BlockEvent]]], type[protocols.Repository]]:

    def func(block_events: Optional[list[protocols.BlockEvent]]) -> type[protocols.Repository]:

        @dataclass
        class FakeBlockEventRepository:

            def __init__(self) -> None:
                self.units = block_events or []

            def add(self, block_event: protocols.BlockEvent) -> protocols.BlockEvent:
                block_event = domain.BlockEvent(
                    status=block_event.status,
                    payment_method_id=block_event.payment_method_id,
                    block_name=block_event.block_name,
                )
                self.units.append(block_event)
                return block_event

            def get(  # type:ignore[empty-body]
                self, id: uuid.UUID
            ) -> protocols.BlockEvent: ...

        return FakeBlockEventRepository

    return func


@pytest.fixture(scope="module")
def fake_unit_of_work() -> type[protocols.UnitOfWork]:

    @dataclass
    class FakeUnitOfWork:
        payment_method_repository_class: type[protocols.Repository]
        payment_methods: protocols.Repository = field(init=False)

        payment_operation_repository_class: type[protocols.Repository]
        payment_operations: protocols.Repository = field(init=False)

        block_event_repository_class: type[protocols.Repository]
        block_events: protocols.Repository = field(init=False)

        transaction_repository_class: type[protocols.Repository]
        transactions: protocols.Repository = field(init=False)

        payment_method_units: list[protocols.PaymentMethod] = field(default_factory=list)
        payment_operation_units: list[protocols.PaymentMethod] = field(default_factory=list)
        block_event_units: list[protocols.BlockEvent] = field(default_factory=list)
        transaction_units: list[protocols.Transaction] = field(default_factory=list)

        def __enter__(self) -> Self:
            self.payment_methods = self.payment_method_repository_class()
            self.payment_operations = self.payment_operation_repository_class()
            self.block_events = self.block_event_repository_class()
            self.transactions = self.transaction_repository_class()
            return self

        def __exit__(
            self,
            exc_type: Optional[type[Exception]],
            exc_value: Optional[type[Exception]],
            exc_tb: Optional[TracebackType],
        ) -> None:
            pass

        def commit(self) -> None:
            self.payment_method_units += self.payment_methods.units  # type:ignore[attr-defined]
            self.payment_method_units += self.payment_methods.units  # type:ignore[attr-defined]
            self.block_event_units += self.block_events.units  # type:ignore[attr-defined]
            self.transaction_units += self.transactions.units  # type:ignore[attr-defined]

        def rollback(self) -> None:
            pass

    return FakeUnitOfWork
