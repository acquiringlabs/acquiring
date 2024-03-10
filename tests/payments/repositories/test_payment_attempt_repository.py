import pytest

from django_acquiring.payments.models import PaymentAttempt
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

    db_payments = PaymentAttempt.objects.all()
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
