import uuid
from datetime import datetime
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
        PaymentAttemptFactory,
        PaymentMethodFactory,
        PaymentOperationFactory,
        TokenFactory,
    )


@skip_if_django_not_installed
@pytest.mark.django_db
def test_givenCorrectData_whenCallingRepositoryAdd_thenPaymentMethodGetsCreated(
    django_assert_num_queries: Callable,
) -> None:

    payment_attempt = PaymentAttemptFactory()
    data = domain.DraftPaymentMethod(
        payment_attempt=payment_attempt.to_domain(),
        confirmable=True,
    )

    with django_assert_num_queries(6):
        result = storage.django.PaymentMethodRepository().add(data)

    db_payment_methods = storage.django.models.PaymentMethod.objects.all()
    assert len(db_payment_methods) == 1
    db_payment_method = db_payment_methods[0]

    assert db_payment_method.id == result.id
    assert db_payment_method.created_at == result.created_at
    assert db_payment_method.to_domain() == result


@skip_if_django_not_installed
@pytest.mark.django_db
def test_givenExistingPaymentMethodRow_whenCallingRepositoryGet_thenPaymentGetsRetrieved(
    django_assert_num_queries: Callable,
) -> None:
    db_payment_attempt = PaymentAttemptFactory()
    db_payment_method = PaymentMethodFactory(payment_attempt=db_payment_attempt)
    TokenFactory.create(
        token=fake.sha256(),
        created_at=timezone.now(),
        payment_method=db_payment_method,
    )
    PaymentOperationFactory.create(
        payment_method_id=db_payment_method.id,
        status=enums.OperationStatusEnum.STARTED,
        type=enums.OperationTypeEnum.INITIALIZE,
    )
    PaymentOperationFactory.create(
        payment_method_id=db_payment_method.id,
        status=enums.OperationStatusEnum.COMPLETED,
        type=enums.OperationTypeEnum.INITIALIZE,
    )

    with django_assert_num_queries(5):
        result = storage.django.PaymentMethodRepository().get(id=db_payment_method.id)

    assert result == db_payment_method.to_domain()


@skip_if_django_not_installed
@pytest.mark.django_db
def test_givenNonExistingPaymentMethodRow_whenCallingRepositoryGet_thenDoesNotExistGetsRaise(
    django_assert_num_queries: Callable,
) -> None:
    payment_attempt = domain.PaymentAttempt(
        id=uuid.uuid4(),
        created_at=datetime.now(),
        amount=10,
        currency="USD",
        payment_method_ids=[],
    )

    payment_method = domain.PaymentMethod(
        id=uuid.uuid4(),
        payment_attempt=payment_attempt,
        created_at=datetime.now(),
        confirmable=False,
    )

    with django_assert_num_queries(2), pytest.raises(domain.PaymentMethod.DoesNotExist):
        storage.django.PaymentMethodRepository().get(id=payment_method.id)
