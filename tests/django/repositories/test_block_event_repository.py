import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from acquiring.enums import OperationStatusEnum
from acquiring.utils import is_django_installed
from tests.django.utils import skip_if_django_not_installed

if is_django_installed():
    from acquiring import domain, models, repositories
    from tests.django.factories import BlockEventFactory, PaymentAttemptFactory, PaymentMethodFactory


@skip_if_django_not_installed
@pytest.mark.django_db
@pytest.mark.parametrize("status", OperationStatusEnum)
def test_givenCorrectData_whenCallingRepositoryAdd_thenBlockEventGetsCreated(
    status: OperationStatusEnum,
) -> None:

    db_payment_method = PaymentMethodFactory(payment_attempt=PaymentAttemptFactory())
    block_event = domain.BlockEvent(
        status=status,
        payment_method_id=db_payment_method.id,
        block_name="test",
    )

    result = repositories.django.BlockEventRepository().add(block_event)

    db_block_events = models.BlockEvent.objects.all()
    assert len(db_block_events) == 1
    db_block_event = db_block_events[0]

    assert db_block_event.to_domain() == result


@skip_if_django_not_installed
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

    result = repositories.django.BlockEventRepository().add(block_event)

    db_block_event = models.BlockEvent.objects.get(
        block_name=block_name, payment_method_id=db_payment_method.id, status=status
    )
    assert db_block_event.to_domain() == result


@skip_if_django_not_installed
@pytest.mark.django_db
def test_givenExistingBlockEventRow_whenCallingRepositoryAdd_thenthenDuplicateErrorGetsRaised() -> None:

    db_payment_method = PaymentMethodFactory(payment_attempt=PaymentAttemptFactory())
    db_block_event = BlockEventFactory(
        status=OperationStatusEnum.PENDING,
        payment_method_id=db_payment_method.id,
        block_name="test",
    )
    block_event = domain.BlockEvent(
        status=db_block_event.status,
        payment_method_id=db_payment_method.id,
        block_name=db_block_event.block_name,
    )

    with pytest.raises(domain.BlockEvent.DuplicateError):
        repositories.django.BlockEventRepository().add(block_event)
