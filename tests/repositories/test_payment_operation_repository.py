import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from django_acquiring import domain, models, repositories
from django_acquiring.enums import OperationStatusEnum, OperationTypeEnum
from tests.repositories.factories import PaymentAttemptFactory, PaymentMethodFactory, PaymentOperationFactory


@pytest.mark.django_db
@given(
    payment_operation_type=st.sampled_from(OperationTypeEnum),
    payment_operation_status=st.sampled_from(OperationStatusEnum),
)
@settings(max_examples=100)
def test_givenExistingPaymentMethodRow_whenCallingRepositoryAdd_thenPaymentOperationGetsCreated(
    payment_operation_type: OperationTypeEnum,
    payment_operation_status: OperationStatusEnum,
) -> None:
    # Given existing payment method row in payment methods table
    db_payment_attempt = PaymentAttemptFactory()
    db_payment_method = PaymentMethodFactory(payment_attempt_id=db_payment_attempt.id)
    payment_method = db_payment_method.to_domain()

    # When calling PaymentOperationRepository.add_payment_operation
    repositories.PaymentOperationRepository().add(
        payment_method=payment_method,
        type=payment_operation_type,
        status=payment_operation_status,
    )

    # Then PaymentOperation gets created
    payment_operation = models.PaymentOperation.objects.get(
        payment_method_id=db_payment_method.id, status=payment_operation_status, type=payment_operation_type
    )

    # And payment method gets the payment operation added after add_payment_operation
    assert len(payment_method.payment_operations) == 1
    assert payment_method.payment_operations[0] == payment_operation.to_domain()


@pytest.mark.django_db
def test_givenExistingPaymentOperationRow_whenCallingRepositoryAdd_thenthenDuplicateErrorGetsRaised() -> None:

    db_payment_attempt = PaymentAttemptFactory()
    db_payment_method = PaymentMethodFactory(payment_attempt_id=db_payment_attempt.id)
    payment_method = db_payment_method.to_domain()

    # given existing payment operation
    PaymentOperationFactory(
        payment_method_id=payment_method.id,
        type=OperationTypeEnum.INITIALIZE,
        status=OperationStatusEnum.STARTED,
    )

    with pytest.raises(domain.PaymentOperation.DuplicateError):
        repositories.PaymentOperationRepository().add(
            payment_method=payment_method,
            type=OperationTypeEnum.INITIALIZE,
            status=OperationStatusEnum.STARTED,
        )
