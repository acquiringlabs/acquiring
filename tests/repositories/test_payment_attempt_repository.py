import uuid
from typing import Callable

import pytest
from django.utils import timezone

from django_acquiring import domain, models, repositories
from tests.factories import OrderFactory, PaymentAttemptFactory, PaymentMethodFactory, PaymentOperationFactory


@pytest.mark.django_db
def test_givenCorrectData_whenCallingRepositoryAdd_thenPaymentAttemptGetsCreated(
    django_assert_num_queries: Callable,
) -> None:

    db_order = OrderFactory()

    data = domain.DraftPaymentAttempt(order_id=db_order.id, amount=999, currency="NZD")

    # When calling PaymentAttemptRepository.add
    with django_assert_num_queries(3):
        result = repositories.PaymentAttemptRepository().add(data)

    # Then PaymentAttempt gets created

    db_payments = models.PaymentAttempt.objects.all()
    assert len(db_payments) == 1
    db_payment = db_payments[0]

    assert db_payment.id == result.id
    assert db_payment.created_at == result.created_at
    assert db_payment.to_domain() == result


@pytest.mark.django_db
def test_givenInCorrectCurrencyData_whenCallingRepositoryAdd_thenPaymentAttemptRaisesError(
    django_assert_num_queries: Callable,
) -> None:
    # Given Incorrect Currency Data
    db_order = OrderFactory()

    data = domain.DraftPaymentAttempt(order_id=db_order.id, amount=999, currency="fake")

    # When calling PaymentAttemptRepository.add
    with django_assert_num_queries(3):  # , pytest.raises(domain.CurrencyField.DoesNotExist):
        result = repositories.PaymentAttemptRepository().add(data)

    # Then PaymentAttempt raises an error

    db_payments = models.PaymentAttempt.objects.all()
    assert len(db_payments) == 1
    db_payment = db_payments[0]

    assert db_payment.id == result.id
    assert db_payment.created_at == result.created_at
    assert db_payment.to_domain() == result


@pytest.mark.django_db
def test_givenExistingPaymentAttemptRowInPaymentAttemptsTable_whenCallingRepositoryGet_thenPaymentAttemptGetsRetrieved(
    django_assert_num_queries: Callable,
) -> None:
    # Given existing payment attempt row in payments table
    db_payment_attempt = PaymentAttemptFactory()
    db_payment_methods = PaymentMethodFactory.create_batch(3, payment_attempt_id=db_payment_attempt.id)
    PaymentOperationFactory.create_batch(3, payment_method_id=db_payment_methods[0].id)

    # When calling PaymentAttemptRepository.get
    with django_assert_num_queries(3):
        result = repositories.PaymentAttemptRepository().get(id=db_payment_attempt.id)

    # Then PaymentAttempt gets retrieved
    assert result == db_payment_attempt.to_domain()


@pytest.mark.django_db
def test_givenNonExistingPaymentAttemptRow_whenCallingRepositoryGet_thenDoesNotExistGetsRaise(
    django_assert_num_queries: Callable,
) -> None:

    payment_method = domain.PaymentAttempt(
        id=uuid.uuid4(),
        order_id=uuid.uuid4(),
        created_at=timezone.now(),
        amount=999,
        currency="NZD",
    )

    with django_assert_num_queries(1), pytest.raises(domain.PaymentAttempt.DoesNotExist):
        repositories.PaymentAttemptRepository().get(id=payment_method.id)
