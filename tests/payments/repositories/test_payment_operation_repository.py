import itertools
from typing import Callable

import pytest

from django_acquiring import models, repositories
from django_acquiring.protocols.enums import OperationStatusEnum, OperationTypeEnum
from tests.factories import PaymentAttemptFactory, PaymentMethodFactory


@pytest.mark.django_db
@pytest.mark.parametrize(
    "payment_operation_type, payment_operation_status",
    itertools.product(OperationTypeEnum, OperationStatusEnum),
)
def test_givenExistingPaymentMethodRowInPaymentMethodsTable_whenCallingRepositoryAdd_thenPaymentOperationGetsCreated(
    django_assert_num_queries: Callable,
    payment_operation_type: OperationTypeEnum,
    payment_operation_status: OperationStatusEnum,
) -> None:
    # Given existing payment method row in payment methods table
    db_payment_attempt = PaymentAttemptFactory()
    db_payment_method = PaymentMethodFactory(payment_attempt_id=db_payment_attempt.id)
    payment_method = db_payment_method.to_domain()

    # When calling PaymentOperationRepository.add_payment_operation
    with django_assert_num_queries(1):
        repositories.PaymentOperationRepository().add(
            payment_method=payment_method,
            type=payment_operation_type,
            status=payment_operation_status,
        )

    # Then PaymentOperation gets created
    assert models.PaymentOperation.objects.count() == 1
    payment_operation = models.PaymentOperation.objects.first()

    # And payment method gets the payment operation added after add_payment_operation
    assert len(payment_method.payment_operations) == 1
    assert payment_method.payment_operations[0] == payment_operation.to_domain()
