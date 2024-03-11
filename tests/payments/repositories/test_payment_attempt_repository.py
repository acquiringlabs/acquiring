import uuid
from datetime import datetime

import pytest

from django_acquiring.payments.domain import PaymentAttempt
from django_acquiring.payments.models import PaymentAttempt as DbPaymentAttempt
from django_acquiring.payments.repositories import PaymentAttemptRepository
from tests.factories import PaymentAttemptFactory, PaymentMethodFactory, PaymentOperationFactory


@pytest.mark.django_db
def test_givenCorrectData_whenCallingRepositoryAdd_thenPaymentAttemptGetsCreated(django_assert_num_queries):
    # Given Correct Data
    data = {}

    # When calling PaymentAttemptRepository.add
    with django_assert_num_queries(2):
        result = PaymentAttemptRepository().add(data)

    # Then PaymentAttempt gets created
    assert result is not None

    db_payments = DbPaymentAttempt.objects.all()
    assert len(db_payments) == 1
    db_payment = db_payments[0]

    assert db_payment.id == result.id
    assert db_payment.created_at == result.created_at
    assert db_payment.to_domain() == result


@pytest.mark.django_db
def test_givenExistingPaymentAttemptRowInPaymentAttemptsTable_whenCallingRepositoryGet_thenPaymentAttemptGetsRetrieved(
    django_assert_num_queries,
):
    # Given existing payment attempt row in payments table
    db_payment_attempt = PaymentAttemptFactory()
    db_payment_methods = PaymentMethodFactory.create_batch(3, payment_attempt_id=db_payment_attempt.id)
    PaymentOperationFactory.create_batch(3, payment_method_id=db_payment_methods[0].id)

    # When calling PaymentAttemptRepository.get
    with django_assert_num_queries(3):
        result = PaymentAttemptRepository().get(id=db_payment_attempt.id)

    # Then PaymentAttempt gets retrieved
    assert result == db_payment_attempt.to_domain()


@pytest.mark.django_db
def test_givenNonExistingPaymentAttemptRow_whenCallingRepositoryGet_thenDoesNotExistGetsRaise(
    django_assert_num_queries,
):
    # Given a non existing payment method
    payment_method = PaymentAttempt(
        id=uuid.uuid4(),
        created_at=datetime.now(),
    )

    # When calling PaymentMethodRepository.get
    with django_assert_num_queries(1), pytest.raises(PaymentAttempt.DoesNotExist):
        PaymentAttemptRepository().get(id=payment_method.id)
