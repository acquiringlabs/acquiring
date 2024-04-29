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
def fake_payment_repository_class() -> Callable[[Optional[list[protocols.PaymentMethod]]], type[protocols.Repository]]:

    def func(payment_methods: Optional[list[protocols.PaymentMethod]] = None) -> type[protocols.Repository]:

        @dataclass
        class FakePaymentMethodRepository:
            units: list = payment_methods or []

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


@pytest.fixture(scope="module")
def fake_payment_method_repository() -> Callable[
    [Optional[List[protocols.PaymentMethod]]],
    protocols.Repository,
]:

    @dataclass
    class FakePaymentMethodRepository:
        units: List[protocols.PaymentMethod]

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

    def build_repository(
        units: Optional[list[protocols.PaymentMethod]] = None,
    ) -> protocols.Repository:
        return FakePaymentMethodRepository(units=units if units else [])

    return build_repository


@pytest.fixture(scope="module")
def fake_payment_operation_repository() -> Callable[
    [Optional[list[protocols.PaymentOperation]]],
    protocols.Repository,
]:

    @dataclass
    class FakePaymentOperationRepository:
        units: list[protocols.PaymentOperation]

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

    def build_repository(
        units: Optional[list[protocols.PaymentOperation]] = None,
    ) -> protocols.Repository:
        return FakePaymentOperationRepository(units=units if units else [])

    return build_repository


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
def fake_block_event_repository() -> Callable[[Optional[list[protocols.BlockEvent]]], protocols.Repository]:

    @dataclass
    class FakeBlockEventRepository:
        units: list[protocols.BlockEvent]

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

    assert issubclass(FakeBlockEventRepository, protocols.Repository)

    def build_repository(
        units: Optional[list[protocols.BlockEvent]] = None,
    ) -> protocols.Repository:
        return FakeBlockEventRepository(units=units if units else [])

    return build_repository
