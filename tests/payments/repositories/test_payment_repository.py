import pytest

from django_acquiring.payments.models import PaymentAttempt
from django_acquiring.payments.repositories import PaymentRepository
from tests.payments.factories import PaymentAttemptFactory


@pytest.mark.django_db
def test_givenCorrectData_whenCallingRepositoryAdd_thenPaymentGetsCreated():
    # Given Correct Data
    data = {}

    # When calling PaymentRepository.add
    result = PaymentRepository().add(data)

    # Then Payment gets created
    assert result is not None

    db_payments = PaymentAttempt.objects.all()
    assert len(db_payments) == 1
    db_payment = db_payments[0]

    assert db_payment.id == result.id
    assert db_payment.created_at == result.created_at
    assert db_payment.to_domain() == result


@pytest.mark.django_db
def test_givenExistingPaymentRowInPaymentsTable_whenCallingRepositoryGet_thenPaymentGetsRetrieved():
    # Given existing payment row in payments table
    db_payment_attempt = PaymentAttemptFactory()

    # When calling PaymentRepository.get
    result = PaymentRepository().get(id=db_payment_attempt.id)

    # Then Payment gets retrieved
    assert result == db_payment_attempt.to_domain()
