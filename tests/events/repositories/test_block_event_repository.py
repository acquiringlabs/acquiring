import pytest

from django_acquiring.events import domain, models, repositories
from django_acquiring.protocols.payments import OperationStatusEnum
from tests.factories import PaymentAttemptFactory, PaymentMethodFactory


@pytest.mark.django_db
@pytest.mark.parametrize("status", OperationStatusEnum)
def test_givenCorrectData_whenCallingRepositoryAdd_thenBlockEventGetsCreated(django_assert_num_queries, status):
    # Given Correct Data
    db_payment_method = PaymentMethodFactory(payment_attempt=PaymentAttemptFactory())
    block_event = domain.BlockEvent(
        status=status,
        payment_method_id=db_payment_method.id,
        block_name="test",
    )

    # When calling PaymentAttemptRepository.add
    with django_assert_num_queries(2):
        result = repositories.BlockEventRepository().add(block_event)

    # Then BlockEvent gets created

    db_block_events = models.BlockEvent.objects.all()
    assert len(db_block_events) == 1
    db_block_event = db_block_events[0]

    assert db_block_event.to_domain() == result