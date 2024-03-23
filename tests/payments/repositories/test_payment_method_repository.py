import uuid
from datetime import datetime, timedelta
from typing import Callable

import pytest
from django.utils import timezone
from faker import Faker

from django_acquiring import domain, models, repositories
from tests.factories import PaymentAttemptFactory, PaymentMethodFactory, PaymentOperationFactory, TokenFactory

fake = Faker()


@pytest.mark.django_db
def test_givenCorrectData_whenCallingRepositoryAdd_thenPaymentMethodGetsCreated(
    django_assert_num_queries: Callable,
) -> None:
    # Given Correct Data
    payment_attempt = PaymentAttemptFactory()
    data = domain.DraftPaymentMethod(
        payment_attempt_id=payment_attempt.id,
        confirmable=True,
    )

    # When calling PaymentMethodRepository.add
    with django_assert_num_queries(4):
        result = repositories.PaymentMethodRepository().add(data)

    # Then PaymentMethod gets created

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
    # Given Correct Data
    payment_attempt = PaymentAttemptFactory()
    data = domain.DraftPaymentMethod(
        payment_attempt_id=payment_attempt.id,
        confirmable=confirmable,
        token=domain.Token(
            created_at=timezone.now(),
            token=fake.sha256(raw_output=False),
            expires_at=timezone.now() + timedelta(days=365),
            fingerprint=fake.sha256(),
            metadata={"customer_id": str(uuid.uuid4())},
        ),
    )

    # When calling PaymentMethodRepository.add
    with django_assert_num_queries(5):
        result = repositories.PaymentMethodRepository().add(data)

    # Then Token gets created

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
    # Given existing payment method row in payment methods table
    db_payment_attempt = PaymentAttemptFactory()
    db_payment_method = PaymentMethodFactory(payment_attempt_id=db_payment_attempt.id)
    db_token = TokenFactory(
        token=fake.sha256(),
        created_at=timezone.now(),
    )
    db_payment_method.token = db_token
    db_payment_method.save()
    PaymentOperationFactory.create_batch(3, payment_method_id=db_payment_method.id)

    # When calling PaymentMethodRepository.get
    with django_assert_num_queries(2):
        result = repositories.PaymentMethodRepository().get(id=db_payment_method.id)

    # Then PaymentMethod gets retrieved
    assert result == db_payment_method.to_domain()


@pytest.mark.django_db
def test_givenNonExistingPaymentMethodRow_whenCallingRepositoryGet_thenDoesNotExistGetsRaise(
    django_assert_num_queries: Callable,
) -> None:
    # Given a non existing payment method
    payment_method = domain.PaymentMethod(
        id=uuid.uuid4(),
        payment_attempt_id=uuid.uuid4(),
        created_at=datetime.now(),
        confirmable=False,
    )

    # When calling PaymentMethodRepository.get
    with django_assert_num_queries(1), pytest.raises(domain.PaymentMethod.DoesNotExist):
        repositories.PaymentMethodRepository().get(id=payment_method.id)


@pytest.mark.django_db
def test_givenCorrectTokenDataAndExistingPaymentMethod_whenCallingRepositoryAddToken_thenTokenGetsCreated(
    django_assert_num_queries: Callable,
) -> None:
    # Given Correct Data
    db_payment_attempt = PaymentAttemptFactory()
    db_payment_method = PaymentMethodFactory(payment_attempt_id=db_payment_attempt.id)
    payment_method = db_payment_method.to_domain()
    token = domain.Token(created_at=timezone.now(), token=fake.sha256())

    # When calling PaymentMethodRepository.add_token
    with django_assert_num_queries(5):
        result = repositories.PaymentMethodRepository().add_token(
            payment_method=payment_method,
            token=token,
        )

    # Then Token gets created
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
    # Given a non existing payment method
    payment_method = domain.PaymentMethod(
        id=uuid.uuid4(),
        payment_attempt_id=uuid.uuid4(),
        created_at=datetime.now(),
        confirmable=False,
    )
    token = domain.Token(created_at=timezone.now(), token=fake.sha256())

    # When calling PaymentMethodRepository.get
    with django_assert_num_queries(1), pytest.raises(domain.PaymentMethod.DoesNotExist):
        repositories.PaymentMethodRepository().add_token(
            payment_method=payment_method,
            token=token,
        )
