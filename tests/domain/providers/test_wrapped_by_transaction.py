import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Callable, Optional, Sequence

from faker import Faker

from acquiring import domain, enums, protocols
from tests.domain import factories

fake = Faker()


def test_givenValidFunction_whenDecoratedWithwrapped_by_transaction_thenTransactionGetsCorrectlyCreated(
    fake_payment_method_repository_class: Callable[
        [Optional[list[protocols.PaymentMethod]]],
        type[protocols.Repository],
    ],
    fake_transaction_repository_class: Callable[
        [Optional[list[protocols.PaymentMethod]]],
        type[protocols.Repository],
    ],
    fake_payment_operation_repository_class: Callable[
        [Optional[list[protocols.PaymentOperation]]],
        type[protocols.Repository],
    ],
    fake_block_event_repository_class: Callable[
        [Optional[list[protocols.PaymentOperation]]],
        type[protocols.Repository],
    ],
    fake_unit_of_work: type[protocols.UnitOfWork],
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

        @domain.wrapped_by_transaction
        def do_something(
            self: protocols.Adapter,
            unit_of_work: protocols.UnitOfWork,
            payment_method: protocols.PaymentMethod,
            *args: Sequence,
            **kwargs: dict,
        ) -> protocols.AdapterResponse:
            """This is the expected doc"""

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

    unit_of_work = fake_unit_of_work(
        payment_method_repository_class=fake_payment_method_repository_class([]),
        payment_operation_repository_class=fake_payment_operation_repository_class([]),
        block_event_repository_class=fake_block_event_repository_class([]),
        transaction_repository_class=fake_transaction_repository_class([]),
    )

    FakeAdapter(
        base_url=fake.url(),
        provider_name=provider_name,
    ).do_something(unit_of_work, payment_method)

    transactions: list[protocols.Transaction] = unit_of_work.transaction_units  # type:ignore[attr-defined]
    assert len(transactions) == 1

    assert transactions[0] == domain.Transaction(
        external_id=external_id,
        timestamp=timestamp,
        raw_data=raw_data,
        provider_name=provider_name,
        payment_method_id=payment_method.id,
    )

    assert FakeAdapter.do_something.__name__ == "do_something"
    assert FakeAdapter.do_something.__doc__ == "This is the expected doc"
