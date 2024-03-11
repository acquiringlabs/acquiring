import uuid
from datetime import datetime

import pytest

from django_acquiring.payments.domain import PaymentMethod
from django_acquiring.payments.models import PaymentMethod as DbPaymentMethod
from django_acquiring.payments.repositories import PaymentMethodRepository
from tests.factories import PaymentAttemptFactory, PaymentMethodFactory, PaymentOperationFactory


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

    db_payment_methods = DbPaymentMethod.objects.all()
    assert len(db_payment_methods) == 1
    db_payment_method = db_payment_methods[0]

    assert db_payment_method.id == result.id
    assert db_payment_method.created_at == result.created_at
    assert db_payment_method.to_domain() == result


@pytest.mark.django_db
def test_givenExistingPaymentMethodRowInPaymentMethodsTable_whenCallingRepositoryGet_thenPaymentGetsRetrieved(
    django_assert_num_queries,
):
    # Given existing payment method row in payment methods table
    db_payment_attempt = PaymentAttemptFactory()
    db_payment_method = PaymentMethodFactory(payment_attempt_id=db_payment_attempt.id)
    PaymentOperationFactory.create_batch(3, payment_method_id=db_payment_method.id)

    # When calling PaymentMethodRepository.get
    with django_assert_num_queries(2):
        result = PaymentMethodRepository().get(id=db_payment_method.id)

    # Then PaymentMethod gets retrieved
    assert result == db_payment_method.to_domain()


@pytest.mark.django_db
def test_givenNonExistingPaymentMethodRow_whenCallingRepositoryGet_thenDoesNotExistGetsRaise(
    django_assert_num_queries,
):
    # Given a non existing payment method
    payment_method = PaymentMethod(
        id=uuid.uuid4(),
        payment_attempt_id=uuid.uuid4(),
        created_at=datetime.now(),
    )

    # When calling PaymentMethodRepository.get
    with django_assert_num_queries(1), pytest.raises(PaymentMethod.DoesNotExist):
        PaymentMethodRepository().get(id=payment_method.id)
