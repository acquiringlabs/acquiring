import uuid
from dataclasses import dataclass
from typing import Callable, Optional, Sequence

from acquiring import domain, enums, protocols
from tests.domain import factories


@dataclass
class FooBlock:

    @domain.wrapped_by_block_events
    def run(
        self,
        unit_of_work: protocols.UnitOfWork,
        payment_method: protocols.PaymentMethod,
        *args: Sequence,
        **kwargs: dict,
    ) -> protocols.BlockResponse:
        """This is the expected doc"""
        return domain.BlockResponse(status=enums.OperationStatusEnum.COMPLETED)


def test_givenValidFunction_whenDecoratedWithwrapped_by_block_events_thenStartedAndCompletedBlockEventsGetsCreated(
    fake_payment_method_repository_class: Callable[
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
    fake_transaction_repository_class: Callable[
        [Optional[list[protocols.PaymentOperation]]],
        type[protocols.Repository],
    ],
    fake_unit_of_work: type[protocols.UnitOfWork],
) -> None:

    unit_of_work = fake_unit_of_work(
        payment_method_repository_class=fake_payment_method_repository_class([]),
        payment_operation_repository_class=fake_payment_operation_repository_class([]),
        block_event_repository_class=fake_block_event_repository_class([]),
        transaction_repository_class=fake_transaction_repository_class([]),
    )

    payment_attempt = factories.PaymentAttemptFactory()
    payment_method_id = uuid.uuid4()
    payment_method = factories.PaymentMethodFactory(
        payment_attempt=payment_attempt,
        id=payment_method_id,
    )

    FooBlock().run(unit_of_work=unit_of_work, payment_method=payment_method)

    block_events: list[domain.BlockEvent] = unit_of_work.block_event_units  # type:ignore[attr-defined]
    assert len(block_events) == 2

    assert block_events[0].status == enums.OperationStatusEnum.STARTED
    assert block_events[0].payment_method_id == payment_method.id
    assert block_events[0].block_name == FooBlock.__name__

    assert block_events[1].status == enums.OperationStatusEnum.COMPLETED
    assert block_events[1].payment_method_id == payment_method.id
    assert block_events[1].block_name == FooBlock.__name__

    # Name and Doc are Preserved
    assert FooBlock.run.__name__ == "run"
    assert FooBlock.run.__doc__ == "This is the expected doc"
