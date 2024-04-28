from itertools import product

import pytest

from acquiring.enums import OperationStatusEnum, OperationTypeEnum
from acquiring.utils import is_django_installed
from tests.storage.utils import skip_if_django_not_installed

if is_django_installed():
    from acquiring import domain, storage
    from tests.storage.django.factories import PaymentAttemptFactory, PaymentMethodFactory, PaymentOperationFactory


@skip_if_django_not_installed
@pytest.mark.django_db
@pytest.mark.parametrize(
    "payment_operation_type, payment_operation_status", product(OperationTypeEnum, OperationStatusEnum)
)
def test_givenExistingPaymentMethodRow_whenCallingRepositoryAdd_thenPaymentOperationGetsCreated(
    payment_operation_type: OperationTypeEnum,
    payment_operation_status: OperationStatusEnum,
) -> None:
    # Given existing payment method row in payment methods table
    db_payment_attempt = PaymentAttemptFactory()
    db_payment_method = PaymentMethodFactory(payment_attempt_id=db_payment_attempt.id)
    payment_method = db_payment_method.to_domain()

    # When calling PaymentOperationRepository.add_payment_operation
    storage.django.PaymentOperationRepository().add(
        payment_method=payment_method,
        type=payment_operation_type,
        status=payment_operation_status,
    )

    # Then PaymentOperation gets created
    payment_operation = storage.django.models.PaymentOperation.objects.get(
        payment_method_id=db_payment_method.id,
        status=payment_operation_status,
        type=payment_operation_type,
    )

    # And payment method gets the payment operation added after add_payment_operation
    assert len(payment_method.payment_operations) == 1
    assert payment_method.payment_operations[0] == payment_operation.to_domain()


@skip_if_django_not_installed
@pytest.mark.django_db
def test_givenExistingPaymentOperationRow_whenCallingRepositoryAdd_thenthenDuplicatedErrorGetsRaised() -> None:

    db_payment_attempt = PaymentAttemptFactory()
    db_payment_method = PaymentMethodFactory(payment_attempt_id=db_payment_attempt.id)
    payment_method = db_payment_method.to_domain()

    # given existing payment operation
    PaymentOperationFactory(
        payment_method_id=payment_method.id,
        type=OperationTypeEnum.INITIALIZE,
        status=OperationStatusEnum.STARTED,
    )

    with pytest.raises(domain.PaymentOperation.Duplicated):
        storage.django.PaymentOperationRepository().add(
            payment_method=payment_method,
            type=OperationTypeEnum.INITIALIZE,
            status=OperationStatusEnum.STARTED,
        )
