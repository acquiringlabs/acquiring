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
        PaymentAttemptFactory,
        PaymentMethodFactory,
        PaymentOperationFactory,
        TokenFactory,
    )


@skip_if_django_not_installed
@pytest.mark.django_db
def test_givenExistingPaymentAttemptRow_whenCallingRepositoryGet_thenPaymentAttemptGetsRetrieved(
    django_assert_num_queries: Callable,
) -> None:
    db_payment_attempt = PaymentAttemptFactory()
    db_payment_method = PaymentMethodFactory(payment_attempt=db_payment_attempt)
    TokenFactory.create(
        token=fake.sha256(),
        timestamp=timezone.now(),
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
        result = storage.django.PaymentAttemptRepository().get(id=db_payment_attempt.id)

    assert result == db_payment_attempt.to_domain()


@skip_if_django_not_installed
@pytest.mark.django_db
def test_givenNonExistingPaymentAttemptRow_whenCallingRepositoryGet_thenDoesNotExistGetsRaise(
    django_assert_num_queries: Callable,
) -> None:

    with django_assert_num_queries(2), pytest.raises(domain.PaymentAttempt.DoesNotExist):
        storage.django.PaymentAttemptRepository().get(id=uuid.uuid4())
