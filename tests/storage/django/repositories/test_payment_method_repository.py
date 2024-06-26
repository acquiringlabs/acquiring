import uuid
from typing import Callable

import pytest
from faker import Faker

from acquiring import enums
from acquiring.utils import is_django_installed
from tests.storage.utils import skip_if_django_not_installed

fake = Faker()

if is_django_installed():
    from django.utils import timezone  # TODO replace with native aware Python datetime object

    from acquiring import domain, storage
    from tests.storage.django.factories import (
        OperationEventFactory,
        PaymentAttemptFactory,
        PaymentMethodFactory,
        TokenFactory,
    )


@skip_if_django_not_installed
@pytest.mark.django_db
def test_givenCorrectData_whenCallingRepositoryAdd_thenPaymentMethodGetsCreated(
    django_assert_num_queries: Callable,
) -> None:

    payment_attempt = PaymentAttemptFactory()
    data = domain.DraftPaymentMethod(
        payment_attempt_id=payment_attempt.id,
    )

    with django_assert_num_queries(3):
        result = storage.django.PaymentMethodRepository().add(data)

    db_payment_methods = storage.django.models.PaymentMethod.objects.all()
    assert len(db_payment_methods) == 1
    db_payment_method = db_payment_methods[0]

    assert db_payment_method.id == result.id
    assert db_payment_method.created_at == result.created_at
    assert db_payment_method.to_domain() == result


@skip_if_django_not_installed
@pytest.mark.django_db
def test_givenExistingPaymentMethodRow_whenCallingRepositoryGet_thenPaymentMethodGetsRetrieved(
    django_assert_num_queries: Callable,
) -> None:
    db_payment_attempt = PaymentAttemptFactory()
    db_payment_method = PaymentMethodFactory(payment_attempt_id=db_payment_attempt.id)
    TokenFactory.create(
        token=fake.sha256(),
        timestamp=timezone.now(),
        payment_method=db_payment_method,
    )
    OperationEventFactory.create(
        payment_method_id=db_payment_method.id,
        status=enums.OperationStatusEnum.STARTED,
        type=enums.OperationTypeEnum.INITIALIZE,
    )
    OperationEventFactory.create(
        payment_method_id=db_payment_method.id,
        status=enums.OperationStatusEnum.COMPLETED,
        type=enums.OperationTypeEnum.INITIALIZE,
    )

    with django_assert_num_queries(3):
        result = storage.django.PaymentMethodRepository().get(id=db_payment_method.id)

    assert result == db_payment_method.to_domain()


@skip_if_django_not_installed
@pytest.mark.django_db
def test_givenNonExistingPaymentMethodRow_whenCallingRepositoryGet_thenDoesNotExistGetsRaise(
    django_assert_num_queries: Callable,
) -> None:

    with django_assert_num_queries(2), pytest.raises(domain.PaymentMethod.DoesNotExist):
        storage.django.PaymentMethodRepository().get(id=uuid.uuid4())
