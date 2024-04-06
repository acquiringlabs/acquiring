import uuid
from typing import Callable, Sequence

import pytest

from django_acquiring import domain, enums, protocols
from tests.domain import factories


@pytest.mark.parametrize("status", enums.OperationStatusEnum)
def test_givenValidFunction_whenDecoratedWithwrapped_by_block_events_thenStartedAndCompletedBlockEventsGetsCreated(  # type:ignore[misc]
    status: enums.OperationStatusEnum,
    fake_block_event_repository: Callable[..., protocols.AbstractRepository],
) -> None:

    repository = fake_block_event_repository()

    class FooBlock:

        @domain.wrapped_by_block_events(block_event_repository=repository)
        def run(
            self, payment_method: protocols.AbstractPaymentMethod, *args: Sequence, **kwargs: dict
        ) -> protocols.AbstractBlockResponse:
            return domain.BlockResponse(status=status)

    payment_attempt = factories.PaymentAttemptFactory()
    payment_method_id = uuid.uuid4()
    payment_method = factories.PaymentMethodFactory(
        payment_attempt=payment_attempt,
        id=payment_method_id,
    )

    FooBlock().run(payment_method=payment_method)

    block_events: list[domain.BlockEvent] = repository.units  # type:ignore[attr-defined]
    assert len(block_events) == 2

    assert block_events[0].status == enums.OperationStatusEnum.STARTED
    assert block_events[0].payment_method_id == payment_method.id
    assert block_events[0].block_name == FooBlock.__name__

    assert block_events[1].status == status
    assert block_events[1].payment_method_id == payment_method.id
    assert block_events[1].block_name == FooBlock.__name__


def test_givenValidFunction_whenDecoratedWithwrapped_by_block_events_thenNameAndDocsArePreserved(  # type:ignore[misc]
    fake_block_event_repository: Callable[..., protocols.AbstractRepository],
) -> None:

    class FooBlock:

        @domain.wrapped_by_block_events(block_event_repository=fake_block_event_repository())
        def run(
            self, payment_method: protocols.AbstractPaymentMethod, *args: Sequence, **kwargs: dict
        ) -> protocols.AbstractBlockResponse:
            """This is the expected doc"""
            return domain.BlockResponse(status=enums.OperationStatusEnum.COMPLETED)

    assert FooBlock.run.__name__ == "run"
    assert FooBlock.run.__doc__ == "This is the expected doc"
