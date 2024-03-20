import uuid
from datetime import datetime

import pytest

from django_acquiring import domain, models, repositories
from tests.factories import PaymentAttemptFactory, PaymentMethodFactory, PaymentOperationFactory


@pytest.mark.django_db
@pytest.mark.parametrize("confirmable", [True, False])
def test_givenCorrectData_whenCallingRepositoryAdd_thenPaymentMethodGetsCreated(django_assert_num_queries, confirmable):
    # Given Correct Data
    payment_attempt = PaymentAttemptFactory()
    data = domain.PendingPaymentMethod(
        payment_attempt_id=payment_attempt.id,
        confirmable=confirmable,
    )

    # When calling PaymentMethodRepository.add
    with django_assert_num_queries(2):
        result = repositories.PaymentMethodRepository().add(data)

    # Then PaymentMethod gets created

    db_payment_methods = models.PaymentMethod.objects.all()
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
        result = repositories.PaymentMethodRepository().get(id=db_payment_method.id)

    # Then PaymentMethod gets retrieved
    assert result == db_payment_method.to_domain()


@pytest.mark.django_db
def test_givenNonExistingPaymentMethodRow_whenCallingRepositoryGet_thenDoesNotExistGetsRaise(
    django_assert_num_queries,
):
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
