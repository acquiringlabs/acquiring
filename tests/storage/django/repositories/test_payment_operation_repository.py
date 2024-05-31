from itertools import product

import pytest

from acquiring import enums
from acquiring.utils import is_django_installed
from tests.storage.utils import skip_if_django_not_installed

if is_django_installed():
    from acquiring import storage
    from tests.storage.django.factories import PaymentAttemptFactory, PaymentMethodFactory


@skip_if_django_not_installed
@pytest.mark.django_db
@pytest.mark.parametrize(
    "operation_type, operation_status", product(enums.OperationTypeEnum, enums.OperationStatusEnum)
)
def test_givenExistingPaymentMethodRow_whenCallingRepositoryAdd_thenPaymentOperationGetsCreated(
    operation_type: enums.OperationTypeEnum,
    operation_status: enums.OperationStatusEnum,
) -> None:
    # Given existing payment method row in payment methods table
    db_payment_attempt = PaymentAttemptFactory()
    db_payment_method = PaymentMethodFactory(payment_attempt_id=db_payment_attempt.id)
    payment_method = db_payment_method.to_domain()

    # When calling PaymentOperationRepository.add_payment_operation
    storage.django.PaymentOperationRepository().add(
        payment_method=payment_method,
        type=operation_type,
        status=operation_status,
    )

    # Then PaymentOperation gets created
    payment_operation = storage.django.models.PaymentOperation.objects.get(
        payment_method_id=db_payment_method.id,
        status=operation_status,
        type=operation_type,
    )

    # And payment method gets the payment operation added after add_payment_operation
    assert len(payment_method.payment_operations) == 1
    assert payment_method.payment_operations[0] == payment_operation.to_domain()
