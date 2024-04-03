import uuid
from datetime import datetime, timedelta
from typing import Callable

import pytest
from django.utils import timezone  # TODO replace with native aware Python datetime object
from faker import Faker

from django_acquiring import domain, enums, models, repositories
from tests.repositories.factories import (
    PaymentAttemptFactory,
    PaymentMethodFactory,
    PaymentOperationFactory,
    TokenFactory,
)

fake = Faker()


@pytest.mark.django_db
def test_givenCorrectData_whenCallingRepositoryAdd_thenPaymentMethodGetsCreated(
    django_assert_num_queries: Callable,
) -> None:

    payment_attempt = PaymentAttemptFactory()
    data = domain.DraftPaymentMethod(
        payment_attempt=payment_attempt.to_domain(),
        confirmable=True,
    )

    with django_assert_num_queries(7):
        result = repositories.PaymentMethodRepository().add(data)

    db_payment_methods = models.PaymentMethod.objects.all()
    assert len(db_payment_methods) == 1
    db_payment_method = db_payment_methods[0]

    assert db_payment_method.id == result.id
    assert db_payment_method.created_at == result.created_at
    assert db_payment_method.to_domain() == result


@pytest.mark.django_db
@pytest.mark.parametrize("confirmable", [True, False])
def test_givenTokenData_whenCallingRepositoryAdd_thenTokenGetsCreated(
    django_assert_num_queries: Callable, confirmable: bool
) -> None:

    payment_attempt = PaymentAttemptFactory()
    data = domain.DraftPaymentMethod(
        payment_attempt=payment_attempt.to_domain(),
        confirmable=confirmable,
        token=domain.Token(
            created_at=timezone.now(),
            token=fake.sha256(raw_output=False),
            expires_at=timezone.now() + timedelta(days=365),
            fingerprint=fake.sha256(),
            metadata={"customer_id": str(uuid.uuid4())},
        ),
    )

    with django_assert_num_queries(8):
        result = repositories.PaymentMethodRepository().add(data)

    db_tokens = models.Token.objects.all()
    assert len(db_tokens) == 1
    db_token = db_tokens[0]

    db_payment_methods = models.PaymentMethod.objects.all()
    assert len(db_payment_methods) == 1
    db_payment_method = db_payment_methods[0]

    assert db_token.payment_method == db_payment_method

    assert result.token == db_token.to_domain()


@pytest.mark.django_db
def test_givenExistingPaymentMethodRowInPaymentMethodsTable_whenCallingRepositoryGet_thenPaymentGetsRetrieved(
    django_assert_num_queries: Callable,
) -> None:
    db_payment_attempt = PaymentAttemptFactory()
    db_payment_method = PaymentMethodFactory(payment_attempt=db_payment_attempt)
    db_token = TokenFactory(
        token=fake.sha256(),
        created_at=timezone.now(),
    )
    db_payment_method.token = db_token
    db_payment_method.save()
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

    with django_assert_num_queries(4):
        result = repositories.PaymentMethodRepository().get(id=db_payment_method.id)

    assert result == db_payment_method.to_domain()


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

    with django_assert_num_queries(1), pytest.raises(domain.PaymentMethod.DoesNotExist):
        repositories.PaymentMethodRepository().get(id=payment_method.id)


@pytest.mark.django_db
def test_givenCorrectTokenDataAndExistingPaymentMethod_whenCallingRepositoryAddToken_thenTokenGetsCreated(
    django_assert_num_queries: Callable,
) -> None:

    db_payment_attempt = PaymentAttemptFactory()
    db_payment_method = PaymentMethodFactory(payment_attempt_id=db_payment_attempt.id)
    payment_method = db_payment_method.to_domain()
    token = domain.Token(created_at=timezone.now(), token=fake.sha256())

    with django_assert_num_queries(5):
        result = repositories.PaymentMethodRepository().add_token(
            payment_method=payment_method,
            token=token,
        )

    db_tokens = models.Token.objects.all()
    assert len(db_tokens) == 1
    db_token = db_tokens[0]

    assert db_token.to_domain() == token
    assert payment_method.token == token

    assert result == payment_method


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
    token = domain.Token(created_at=timezone.now(), token=fake.sha256())

    with django_assert_num_queries(1), pytest.raises(domain.PaymentMethod.DoesNotExist):
        repositories.PaymentMethodRepository().add_token(
            payment_method=payment_method,
            token=token,
        )
