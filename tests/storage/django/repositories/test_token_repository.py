import uuid
from datetime import datetime
from typing import Callable

import pytest
from faker import Faker

from acquiring.utils import is_django_installed
from tests.storage.utils import skip_if_django_not_installed

fake = Faker()

if is_django_installed():
    from django.utils import timezone  # TODO replace with native aware Python datetime object

    from acquiring import domain, storage
    from tests.storage.django.factories import PaymentAttemptFactory, PaymentMethodFactory


# TODO Add test for adding token to a payment method with an already existing token
@skip_if_django_not_installed
@pytest.mark.django_db
def test_givenCorrectTokenDataAndExistingPaymentMethod_whenCallingRepositoryAdd_thenTokenGetsCreated(
    django_assert_num_queries: Callable,
) -> None:

    db_payment_attempt = PaymentAttemptFactory()
    db_payment_method = PaymentMethodFactory(payment_attempt_id=db_payment_attempt.id)
    payment_method = db_payment_method.to_domain()
    token = domain.Token(payment_method_id=payment_method.id, timestamp=timezone.now(), token=fake.sha256())

    with django_assert_num_queries(2):
        result = storage.django.TokenRepository().add(
            payment_method=payment_method,
            token=token,
        )

    db_tokens = storage.django.models.Token.objects.all()
    assert len(db_tokens) == 1
    db_token = db_tokens[0]

    assert db_token.to_domain() == token

    assert len(payment_method.tokens) == 1
    assert payment_method.tokens[0] == token

    assert result == payment_method


@skip_if_django_not_installed
@pytest.mark.django_db
def test_givenNonExistingPaymentMethodRow_whenCallingRepositoryAdd_thenDoesNotExistGetsRaise(
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
    token = domain.Token(payment_method_id=payment_method.id, timestamp=timezone.now(), token=fake.sha256())

    with django_assert_num_queries(2), pytest.raises(domain.PaymentMethod.DoesNotExist):
        storage.django.TokenRepository().add(
            payment_method=payment_method,
            token=token,
        )
