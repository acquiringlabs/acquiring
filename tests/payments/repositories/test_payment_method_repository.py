import pytest

from django_acquiring.payments.models import PaymentMethod
from django_acquiring.payments.repositories import PaymentMethodRepository
from tests.payments.factories import PaymentAttemptFactory, PaymentMethodFactory, StageEventFactory


@pytest.mark.django_db
def test_givenCorrectData_whenCallingRepositoryAdd_thenPaymentMethodGetsCreated(django_assert_num_queries):
    # Given Correct Data
    payment_attempt = PaymentAttemptFactory()
    data = {
        "payment_attempt_id": payment_attempt.id,
    }

    # When calling PaymentMethodRepository.add
    with django_assert_num_queries(2):
        result = PaymentMethodRepository().add(data)

    # Then PaymentMethod gets created
    assert result is not None

    db_payment_methods = PaymentMethod.objects.all()
    assert len(db_payment_methods) == 1
    db_payment_method = db_payment_methods[0]

    assert db_payment_method.id == result.id
    assert db_payment_method.created_at == result.created_at
    assert db_payment_method.to_domain() == result


@pytest.mark.django_db
def test_givenExistingPaymentMethodRowInPaymentMethodsTable_whenCallingRepositoryGet_thenPaymentGetsRetrieved(
    django_assert_num_queries,
):
    # Given existing payment method row in payments table
    db_payment_attempt = PaymentAttemptFactory()
    db_payment_method = PaymentMethodFactory(payment_attempt_id=db_payment_attempt.id)
    StageEventFactory.create_batch(3, payment_method_id=db_payment_method.id)

    # When calling PaymentMethodRepository.get
    with django_assert_num_queries(2):
        result = PaymentMethodRepository().get(id=db_payment_method.id)

    # Then PaymentMethod gets retrieved
    assert result == db_payment_method.to_domain()


@pytest.mark.django_db
def test_givenExistingPaymentMethodRowInPaymentMethodsTable_whenCallingRepositoryAddStageEvent_thenStageEventGetsCreated(
    django_assert_num_queries,
):
    pass
