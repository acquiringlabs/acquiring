import itertools

import pytest

from django_acquiring.payments.models import PaymentOperation as DbPaymentOperation
from django_acquiring.payments.repositories import PaymentOperationRepository
from django_acquiring.protocols.payments import PaymentOperationStatusEnum, PaymentOperationTypeEnum
from tests.factories import PaymentAttemptFactory, PaymentMethodFactory


@pytest.mark.django_db
@pytest.mark.parametrize(
    "payment_operation_type, payment_operation_status",
    itertools.product(PaymentOperationTypeEnum, PaymentOperationStatusEnum),
)
def test_givenExistingPaymentMethodRowInPaymentMethodsTable_whenCallingRepositoryAdd_thenPaymentOperationGetsCreated(
    django_assert_num_queries,
    payment_operation_type,
    payment_operation_status,
):
    # Given existing payment method row in payment methods table
    db_payment_attempt = PaymentAttemptFactory()
    db_payment_method = PaymentMethodFactory(payment_attempt_id=db_payment_attempt.id)
    payment_method = db_payment_method.to_domain()

    # When calling PaymentOperationRepository.add_payment_operation
    with django_assert_num_queries(1):
        PaymentOperationRepository().add(
            payment_method=payment_method, type=payment_operation_type, status=payment_operation_status
        )

    # Then PaymentOperation gets created
    assert DbPaymentOperation.objects.count() == 1
    payment_operation = DbPaymentOperation.objects.first()

    # And payment method gets the payment operation added after add_payment_operation
    assert payment_method.payment_operations[0] == payment_operation.to_domain()
