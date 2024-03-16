from datetime import datetime
from uuid import uuid4

import pytest

from django_acquiring.flows import PaymentFlow
from django_acquiring.flows.domain import decision_logic as dl
from django_acquiring.payments import domain, models
from django_acquiring.protocols.payments import PaymentOperationStatusEnum, PaymentOperationTypeEnum
from tests.factories import PaymentAttemptFactory, PaymentMethodFactory, PaymentOperationFactory

COMPLETED_STATUS = [PaymentOperationStatusEnum.completed]

FAILED_STATUS = [
    PaymentOperationStatusEnum.started,
    PaymentOperationStatusEnum.requires_action,
    PaymentOperationStatusEnum.failed,
    PaymentOperationStatusEnum.pending,
]


def test_statusListsAreComplete():
    assert set(COMPLETED_STATUS + FAILED_STATUS) == set(PaymentOperationStatusEnum)


@pytest.mark.django_db
@pytest.mark.parametrize(
    "result_status, payment_operation_status",
    [(PaymentOperationStatusEnum.completed, status) for status in COMPLETED_STATUS]
    + [(PaymentOperationStatusEnum.failed, status) for status in FAILED_STATUS],
)
def test_givenAValidPaymentMethod_whenAfterPaying_thenPaymentFlowReturnsTheCorrectOperationResponse(
    fake_payment_method_repository,
    fake_payment_operation_repository,
    fake_block,
    fake_process_actions_block,
    result_status,
    payment_operation_status,
):
    # given a valid payment attempt
    db_payment_attempt = PaymentAttemptFactory.create()
    db_payment_method = PaymentMethodFactory.create(payment_attempt_id=db_payment_attempt.id)

    PaymentOperationFactory(
        type=PaymentOperationTypeEnum.initialize,
        status=PaymentOperationStatusEnum.started,
        payment_method_id=db_payment_method.id,
    ),
    PaymentOperationFactory(
        type=PaymentOperationTypeEnum.initialize,
        status=PaymentOperationStatusEnum.completed,
        payment_method_id=db_payment_method.id,
    ),
    PaymentOperationFactory(
        type=PaymentOperationTypeEnum.pay,
        status=PaymentOperationStatusEnum.started,
        payment_method_id=db_payment_method.id,
    ),
    PaymentOperationFactory(
        type=PaymentOperationTypeEnum.pay,
        status=PaymentOperationStatusEnum.completed,
        payment_method_id=db_payment_method.id,
    ),

    # when after paying
    payment_method_repository = fake_payment_method_repository(db_payment_methods=[db_payment_method])
    payment_flow = PaymentFlow(
        repository=payment_method_repository,
        operations_repository=fake_payment_operation_repository(),
        initialize_block=fake_block(),
        process_actions_block=fake_process_actions_block(),
        pay_blocks=[],
        after_pay_blocks=[fake_block(fake_response_status=payment_operation_status)],
    )

    result = payment_flow.after_pay(db_payment_method.to_domain())

    # then the payment flow returns the correct Operation Response
    assert models.PaymentOperation.objects.count() == 6
    db_payment_operations = models.PaymentOperation.objects.order_by("created_at").all()
    assert db_payment_operations[0].type == PaymentOperationTypeEnum.initialize
    assert db_payment_operations[0].status == PaymentOperationStatusEnum.started

    assert db_payment_operations[1].type == PaymentOperationTypeEnum.initialize
    assert db_payment_operations[1].status == PaymentOperationStatusEnum.completed

    assert db_payment_operations[2].type == PaymentOperationTypeEnum.pay
    assert db_payment_operations[2].status == PaymentOperationStatusEnum.started

    assert db_payment_operations[3].type == PaymentOperationTypeEnum.pay
    assert db_payment_operations[3].status == PaymentOperationStatusEnum.completed

    assert db_payment_operations[4].type == PaymentOperationTypeEnum.after_pay
    assert db_payment_operations[4].status == PaymentOperationStatusEnum.started

    assert db_payment_operations[5].type == PaymentOperationTypeEnum.after_pay
    assert db_payment_operations[5].status == result_status

    assert result.payment_operation_type == PaymentOperationTypeEnum.after_pay
    assert result.status == result_status
    assert result.actions == []
    assert result.payment_method.id == db_payment_method.id


@pytest.mark.django_db
def test_givenAPaymentMethodThatCannotAfterPay_whenAfterPaying_thenPaymentFlowReturnsAFailedStatusOperationResponse(
    fake_payment_method_repository,
    fake_payment_operation_repository,
    fake_block,
    fake_process_actions_block,
):
    # Given a payment method that cannot initialize
    db_payment_attempt = PaymentAttemptFactory.create()
    db_payment_method = PaymentMethodFactory.create(payment_attempt_id=db_payment_attempt.id)
    PaymentOperationFactory.create(
        payment_method_id=db_payment_method.id,
        type=PaymentOperationTypeEnum.initialize,
        status=PaymentOperationStatusEnum.started,
    )
    assert dl.can_after_pay(db_payment_method.to_domain()) is False

    # When After Paying
    payment_method_repository = fake_payment_method_repository(db_payment_methods=[db_payment_method])
    result = PaymentFlow(
        repository=payment_method_repository,
        operations_repository=fake_payment_operation_repository(),
        initialize_block=fake_block(),
        process_actions_block=fake_process_actions_block(),
        pay_blocks=[],
        after_pay_blocks=[],
    ).after_pay(db_payment_method.to_domain())

    # then the payment flow returns a failed status operation response
    assert result.payment_operation_type == PaymentOperationTypeEnum.after_pay
    assert result.status == PaymentOperationStatusEnum.failed
    result.error_message == "PaymentMethod cannot go through this operation"


@pytest.mark.django_db
def test_givenANonExistingPaymentMethod_whenInitializing_thenPaymentFlowReturnsAFailedStatusOperationResponse(
    fake_payment_method_repository,
    fake_payment_operation_repository,
    fake_block,
    fake_process_actions_block,
):
    # Given a non existing payment method
    payment_method = domain.PaymentMethod(
        id=uuid4(),
        created_at=datetime.now(),
        payment_attempt_id=uuid4(),
    )

    # When After Paying
    payment_method_repository = fake_payment_method_repository()
    result = PaymentFlow(
        repository=payment_method_repository,
        operations_repository=fake_payment_operation_repository(),
        initialize_block=fake_block(),
        process_actions_block=fake_process_actions_block(),
        pay_blocks=[],
        after_pay_blocks=[],
    ).after_pay(payment_method)

    # then the payment flow returns a failed status operation response
    assert result.payment_operation_type == PaymentOperationTypeEnum.after_pay
    assert result.status == PaymentOperationStatusEnum.failed
    result.error_message == "PaymentMethod not found"
