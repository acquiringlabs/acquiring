import itertools

import pytest

from django_acquiring.payments.models import PaymentMethod as DbPaymentMethod
from django_acquiring.payments.models import PaymentOperation as DbPaymentOperation
from django_acquiring.payments.protocols import PaymentOperationStatusEnum, PaymentOperationTypeEnum
from django_acquiring.payments.repositories import PaymentMethodRepository
from tests.payments.factories import PaymentAttemptFactory, PaymentMethodFactory, PaymentOperationFactory


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
@pytest.mark.parametrize(
    "payment_operation_type, payment_operation_status",
    itertools.product(PaymentOperationTypeEnum, PaymentOperationStatusEnum),
)
def test_givenExistingPaymentMethodRowInPaymentMethodsTable_whenCallingRepositoryAddPaymentOperation_thenPaymentOperationGetsCreated(
    django_assert_num_queries,
    payment_operation_type,
    payment_operation_status,
):
    # Given existing payment method row in payment methods table
    db_payment_attempt = PaymentAttemptFactory()
    db_payment_method = PaymentMethodFactory(payment_attempt_id=db_payment_attempt.id)
    payment_method = db_payment_method.to_domain()

    # When calling PaymentMethodRepository.add_payment_operation
    with django_assert_num_queries(1):
        PaymentMethodRepository().add_payment_operation(
            payment_method=payment_method, type=payment_operation_type, status=payment_operation_status
        )

    # Then PaymentOperation gets created
    assert DbPaymentOperation.objects.count() == 1
    payment_operation = DbPaymentOperation.objects.first()

    # And payment method gets the payment operation added after add_payment_operation
    assert payment_method.payment_operations[0] == payment_operation.to_domain()
