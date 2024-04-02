from typing import Callable

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from django_acquiring import domain, models, repositories
from django_acquiring.enums import OperationStatusEnum
from tests.repositories.factories import PaymentAttemptFactory, PaymentMethodFactory


@pytest.mark.django_db
@pytest.mark.parametrize("status", OperationStatusEnum)
def test_givenCorrectData_whenCallingRepositoryAdd_thenBlockEventGetsCreated(
    django_assert_num_queries: Callable, status: OperationStatusEnum
) -> None:

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


@pytest.mark.django_db
@given(block_name=st.text(), status=st.sampled_from(OperationStatusEnum))
@settings(max_examples=100)
def test_givenAllData_whenCallingRepositoryAdd_thenBlockEventGetsCreated(
    block_name: str, status: OperationStatusEnum
) -> None:

    db_payment_method = PaymentMethodFactory(payment_attempt=PaymentAttemptFactory())
    block_event = domain.BlockEvent(
        status=status,
        payment_method_id=db_payment_method.id,
        block_name=block_name,
    )

    result = repositories.BlockEventRepository().add(block_event)

    db_block_event = models.BlockEvent.objects.get(
        block_name=block_name, payment_method_id=db_payment_method.id, status=status
    )
    assert db_block_event.to_domain() == result
