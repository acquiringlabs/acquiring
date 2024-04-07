import os
import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Callable, Generator, List, Optional
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
            DATABASES={
                "default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"},
                "secondary": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"},
            },
            INSTALLED_APPS=project_settings.INSTALLED_APPS,
            MIGRATION_MODULES={"acquiring": "acquiring.migrations.django"},
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
        },
    ):
        yield


@pytest.fixture(scope="module")
def fake_payment_method_repository() -> Callable[
    [Optional[List[protocols.AbstractPaymentMethod]]],
    protocols.AbstractRepository,
]:

    @dataclass
    class FakePaymentMethodRepository:
        units: List[protocols.AbstractPaymentMethod]

        def add(self, data: protocols.AbstractDraftPaymentMethod) -> protocols.AbstractPaymentMethod:
            payment_method = domain.PaymentMethod(
                id=uuid.uuid4(),
                created_at=datetime.now(),
                payment_attempt=data.payment_attempt,
                confirmable=data.confirmable,
                token=data.token,
                payment_operations=[],
            )
            self.units.append(payment_method)
            return payment_method

        def get(self, id: uuid.UUID) -> protocols.AbstractPaymentMethod:
            for unit in self.units:
                if unit.id == id:
                    return unit
            raise domain.PaymentMethod.DoesNotExist

    def build_repository(
        units: Optional[list[protocols.AbstractPaymentMethod]] = None,
    ) -> protocols.AbstractRepository:
        return FakePaymentMethodRepository(units=units if units else [])

    return build_repository


@pytest.fixture(scope="module")
def fake_payment_operation_repository() -> Callable[
    [Optional[list[protocols.AbstractPaymentOperation]]],
    protocols.AbstractRepository,
]:

    @dataclass
    class FakePaymentOperationRepository:
        units: list[protocols.AbstractPaymentOperation]

        def add(
            self,
            payment_method: protocols.AbstractPaymentMethod,
            type: enums.OperationTypeEnum,
            status: enums.OperationStatusEnum,
        ) -> protocols.AbstractPaymentOperation:
            payment_operation = domain.PaymentOperation(
                type=type,
                status=status,
                payment_method_id=payment_method.id,
            )
            payment_method.payment_operations.append(payment_operation)
            return payment_operation

        def get(  # type:ignore[empty-body]
            self, id: uuid.UUID
        ) -> protocols.AbstractPaymentOperation: ...

    def build_repository(
        units: Optional[list[protocols.AbstractPaymentOperation]] = None,
    ) -> protocols.AbstractRepository:
        return FakePaymentOperationRepository(units=units if units else [])

    return build_repository


@pytest.fixture(scope="module")
def fake_transaction_repository() -> Callable[
    [Optional[List[protocols.AbstractTransaction]]],
    protocols.AbstractRepository,
]:

    @dataclass
    class FakeAbstractTransactionRepository:
        units: List[protocols.AbstractTransaction]

        def add(self, transaction: protocols.AbstractTransaction) -> protocols.AbstractTransaction:
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
        ) -> protocols.AbstractTransaction: ...

    def build_repository(
        units: Optional[list[protocols.AbstractTransaction]] = None,
    ) -> protocols.AbstractRepository:
        return FakeAbstractTransactionRepository(units=units if units else [])

    return build_repository


@pytest.fixture(scope="module")
def fake_block_event_repository() -> (
    Callable[[Optional[list[protocols.AbstractBlockEvent]]], protocols.AbstractRepository]
):

    @dataclass
    class FakeBlockEventRepository:
        units: list[protocols.AbstractBlockEvent]

        def add(self, block_event: protocols.AbstractBlockEvent) -> protocols.AbstractBlockEvent:
            block_event = domain.BlockEvent(
                status=block_event.status,
                payment_method_id=block_event.payment_method_id,
                block_name=block_event.block_name,
            )
            self.units.append(block_event)
            return block_event

        def get(  # type:ignore[empty-body]
            self, id: uuid.UUID
        ) -> protocols.AbstractBlockEvent: ...

    assert issubclass(FakeBlockEventRepository, protocols.AbstractRepository)

    def build_repository(
        units: Optional[list[protocols.AbstractBlockEvent]] = None,
    ) -> protocols.AbstractRepository:
        return FakeBlockEventRepository(units=units if units else [])

    return build_repository
