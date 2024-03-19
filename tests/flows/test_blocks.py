import pytest

from django_acquiring.events import models
from django_acquiring.flows import domain
from django_acquiring.protocols.enums import OperationStatusEnum
from django_acquiring.protocols.flows import AbstractBlock, AbstractBlockResponse
from django_acquiring.protocols.payments import AbstractPaymentMethod
from tests.factories import PaymentAttemptFactory, PaymentMethodFactory


@pytest.mark.django_db
@pytest.mark.parametrize("status", OperationStatusEnum)
def test_givenValidFunction_whenDecoratedWithwrapped_by_block_events_thenStartedAndCompletedBlockEventsGetsCreated(
    status, django_assert_num_queries
):

    class FooBlock:
        @domain.wrapped_by_block_events
        def run(self, payment_method: AbstractPaymentMethod, *args, **kwargs) -> AbstractBlockResponse:
            return domain.BlockResponse(status=status, payment_method=payment_method)

    assert issubclass(FooBlock, AbstractBlock)

    payment_method = PaymentMethodFactory(payment_attempt=PaymentAttemptFactory())

    with django_assert_num_queries(4):
        FooBlock().run(payment_method=payment_method)

    assert models.BlockEvent.objects.count() == 2

    block_events = models.BlockEvent.objects.order_by("created_at")

    assert block_events[0].status == OperationStatusEnum.started
    assert block_events[0].payment_method_id == payment_method.id
    assert block_events[0].block_name == FooBlock.__name__

    assert block_events[1].status == status
    assert block_events[1].payment_method_id == payment_method.id
    assert block_events[1].block_name == FooBlock.__name__
