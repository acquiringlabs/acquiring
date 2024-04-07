import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Callable, Optional, Sequence

from faker import Faker

from acquiring import domain, enums, protocols
from tests.domain import factories

fake = Faker()


def test_givenValidFunction_whenDecoratedWithwrapped_by_transaction_thenTransactionGetsCorrectlyCreated(  # type:ignore[misc]
    fake_transaction_repository: Callable[
        ...,
        protocols.AbstractRepository,
    ],
) -> None:

    external_id = "external"
    timestamp = datetime.now()
    raw_data = fake.pydict()
    provider_name = fake.company()

    @dataclass(match_args=False)
    class FakeAdapterResponse:
        external_id: Optional[str]
        timestamp: Optional[datetime]
        raw_data: dict
        status: str

    @dataclass
    class FakeAdapter:
        base_url: str
        provider_name: str
        transaction_repository: protocols.AbstractRepository

        @domain.wrapped_by_transaction
        def do_something(
            self: protocols.AbstractAdapter,
            payment_method: protocols.AbstractPaymentMethod,
            *args: Sequence,
            **kwargs: dict,
        ) -> protocols.AbstractAdapterResponse:

            return FakeAdapterResponse(
                external_id=external_id,
                timestamp=timestamp,
                raw_data=raw_data,
                status=enums.OperationStatusEnum.COMPLETED,
            )

    payment_attempt = factories.PaymentAttemptFactory()
    payment_method_id = uuid.uuid4()
    payment_method = factories.PaymentMethodFactory(
        payment_attempt=payment_attempt,
        id=payment_method_id,
        confirmable=True,
    )

    transaction_repository = fake_transaction_repository()

    FakeAdapter(
        base_url=fake.url(),
        provider_name=provider_name,
        transaction_repository=transaction_repository,
    ).do_something(payment_method)

    transactions: list[protocols.AbstractTransaction] = transaction_repository.units  # type:ignore[attr-defined]
    assert len(transactions) == 1

    assert transactions[0] == domain.Transaction(
        external_id=external_id,
        timestamp=timestamp,
        raw_data=raw_data,
        provider_name=provider_name,
        payment_method_id=payment_method.id,
    )


def test_givenValidFunction_whenDecoratedWithwrapped_by_transaction_thenNameAndDocsArePreserved() -> None:

    @dataclass(match_args=False)
    class FakeAdapterResponse:
        external_id: Optional[str]
        timestamp: Optional[datetime]
        raw_data: dict
        status: str

    @dataclass
    class FakeAdapter:
        base_url: str
        provider_name: str
        transaction_repository: protocols.AbstractRepository

        @domain.wrapped_by_transaction
        def do_something(
            self: protocols.AbstractAdapter,
            payment_method: protocols.AbstractPaymentMethod,
            *args: Sequence,
            **kwargs: dict,
        ) -> protocols.AbstractAdapterResponse:
            """This is the expected doc"""

            return FakeAdapterResponse(
                external_id="external",
                timestamp=datetime.now(),
                raw_data=fake.pydict(),
                status=enums.OperationStatusEnum.COMPLETED,
            )

    assert FakeAdapter.do_something.__name__ == "do_something"
    assert FakeAdapter.do_something.__doc__ == "This is the expected doc"
