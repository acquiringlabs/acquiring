import uuid
from datetime import datetime, timedelta
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

    with django_assert_num_queries(8):
        result = storage.django.PaymentMethodRepository().add(data)

    db_payment_methods = storage.django.models.PaymentMethod.objects.all()
    assert len(db_payment_methods) == 1
    db_payment_method = db_payment_methods[0]

    assert db_payment_method.id == result.id
    assert db_payment_method.created_at == result.created_at
    assert db_payment_method.to_domain() == result


@skip_if_django_not_installed
@pytest.mark.django_db
def test_givenTokenData_whenCallingRepositoryAdd_thenTokenGetsCreated(django_assert_num_queries: Callable) -> None:

    payment_attempt = PaymentAttemptFactory()
    data = domain.DraftPaymentMethod(
        payment_attempt=payment_attempt.to_domain(),
        confirmable=False,
        tokens=[
            domain.DraftToken(
                created_at=timezone.now(),
                token=fake.sha256(raw_output=False),
                expires_at=timezone.now() + timedelta(days=365),
                fingerprint=fake.sha256(),
                metadata={"customer_id": str(uuid.uuid4())},
            ),
        ],
    )

    with django_assert_num_queries(9):
        result = storage.django.PaymentMethodRepository().add(data)

    db_tokens = storage.django.models.Token.objects.all()
    assert len(db_tokens) == 1
    db_token = db_tokens[0]

    db_payment_methods = storage.django.models.PaymentMethod.objects.all()
    assert len(db_payment_methods) == 1
    db_payment_method = db_payment_methods[0]

    assert db_token.payment_method == db_payment_method

    assert len(result.tokens) == 1
    assert result.tokens[0] == db_token.to_domain()


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


@skip_if_django_not_installed
@pytest.mark.django_db
def test_givenCorrectTokenDataAndExistingPaymentMethod_whenCallingRepositoryAddToken_thenTokenGetsCreated(
    django_assert_num_queries: Callable,
) -> None:

    db_payment_attempt = PaymentAttemptFactory()
    db_payment_method = PaymentMethodFactory(payment_attempt_id=db_payment_attempt.id)
    payment_method = db_payment_method.to_domain()
    token = domain.Token(payment_method_id=payment_method.id, created_at=timezone.now(), token=fake.sha256())

    with django_assert_num_queries(5):
        result = storage.django.PaymentMethodRepository().add_token(
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
def test_givenNonExistingPaymentMethodRow_whenCallingRepositoryAddToken_thenDoesNotExistGetsRaise(
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
    token = domain.Token(payment_method_id=payment_method.id, created_at=timezone.now(), token=fake.sha256())

    with django_assert_num_queries(2), pytest.raises(domain.PaymentMethod.DoesNotExist):
        storage.django.PaymentMethodRepository().add_token(
            payment_method=payment_method,
            token=token,
        )
