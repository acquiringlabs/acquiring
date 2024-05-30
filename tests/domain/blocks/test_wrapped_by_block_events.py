import uuid
from dataclasses import dataclass
from typing import Callable, Optional, Sequence
from acquiring import domain, enums, protocols
from tests import protocols as test_protocols
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
        [Optional[set[protocols.PaymentOperation]]],
        type[test_protocols.FakeRepository],
    ],
    fake_block_event_repository_class: Callable[
        [Optional[set[protocols.BlockEvent]]],
        type[test_protocols.FakeRepository],
    ],
    fake_transaction_repository_class: Callable[
        [Optional[set[protocols.Transaction]]],
        type[test_protocols.FakeRepository],
    ],
    fake_unit_of_work: type[test_protocols.FakeUnitOfWork],
) -> None:

    unit_of_work = fake_unit_of_work(
        payment_method_repository_class=fake_payment_method_repository_class([]),
        payment_operation_repository_class=fake_payment_operation_repository_class(set()),
        block_event_repository_class=fake_block_event_repository_class(set()),
        transaction_repository_class=fake_transaction_repository_class(set()),
    )

    payment_attempt = factories.PaymentAttemptFactory()
    payment_method_id = uuid.uuid4()
    payment_method = factories.PaymentMethodFactory(
        payment_attempt=payment_attempt,
        id=payment_method_id,
    )

    FooBlock().run(unit_of_work=unit_of_work, payment_method=payment_method)

    block_events = unit_of_work.block_event_units
    assert len(block_events) == 2

    assert sorted([be.status for be in block_events]) == [
        enums.OperationStatusEnum.COMPLETED,
        enums.OperationStatusEnum.STARTED,
    ]
    assert all([be.payment_method_id == payment_method.id for be in block_events])
    assert all([be.block_name == FooBlock.__name__ for be in block_events])

    # Name and Doc are Preserved
    assert FooBlock.run.__name__ == "run"
    assert FooBlock.run.__doc__ == "This is the expected doc"
