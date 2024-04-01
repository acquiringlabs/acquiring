import uuid
from dataclasses import dataclass

from typing import Callable, Optional

import pytest

from django_acquiring import domain, protocols


@pytest.fixture(scope="module")
def fake_transaction_repository() -> Callable[
    [Optional[list[protocols.AbstractTransaction]]],
    protocols.AbstractRepository,
]:

    @dataclass
    class FakeAbstractTransactionRepository:
        units: list[protocols.AbstractTransaction]

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

    assert issubclass(FakeAbstractTransactionRepository, protocols.AbstractRepository)

    def build_repository(
        units: Optional[list[protocols.AbstractTransaction]] = None,
    ) -> protocols.AbstractRepository:
        return FakeAbstractTransactionRepository(units=units if units else [])

    return build_repository
