from datetime import datetime
from uuid import uuid4

import pytest

from django_acquiring import domain, models
from django_acquiring.domain import decision_logic as dl
from django_acquiring.protocols.enums import OperationStatusEnum, OperationTypeEnum
from tests.factories import PaymentAttemptFactory, PaymentMethodFactory, PaymentOperationFactory

COMPLETED_STATUS = [OperationStatusEnum.completed]

PENDING_STATUS = [OperationStatusEnum.pending]

FAILED_STATUS = [
    OperationStatusEnum.started,
    OperationStatusEnum.requires_action,
    OperationStatusEnum.failed,
]


def test_statusListsAreComplete():
    assert set(COMPLETED_STATUS + PENDING_STATUS + FAILED_STATUS) == set(OperationStatusEnum)


@pytest.mark.django_db
@pytest.mark.parametrize(
    "result_status, payment_operation_status",
    [(OperationStatusEnum.completed, status) for status in COMPLETED_STATUS]
    + [(OperationStatusEnum.pending, status) for status in PENDING_STATUS]
    + [(OperationStatusEnum.failed, status) for status in FAILED_STATUS],
)
def test_givenAValidPaymentMethod_whenConfirmingCompletes_thenPaymentFlowReturnsTheCorrectOperationResponse(
    fake_payment_method_repository,
    fake_payment_operation_repository,
    fake_block,
    fake_process_actions_block,
    result_status,
    payment_operation_status,
):
    # given a valid payment attempt
    db_payment_attempt = PaymentAttemptFactory.create()
    db_payment_method = PaymentMethodFactory.create(
        payment_attempt_id=db_payment_attempt.id,
        confirmable=True,
    )

    PaymentOperationFactory(
        type=OperationTypeEnum.initialize,
        status=OperationStatusEnum.started,
        payment_method_id=db_payment_method.id,
    ),
    PaymentOperationFactory(
        type=OperationTypeEnum.initialize,
        status=OperationStatusEnum.completed,
        payment_method_id=db_payment_method.id,
    ),
    PaymentOperationFactory(
        type=OperationTypeEnum.pay,
        status=OperationStatusEnum.started,
        payment_method_id=db_payment_method.id,
    ),
    PaymentOperationFactory(
        type=OperationTypeEnum.pay,
        status=OperationStatusEnum.completed,
        payment_method_id=db_payment_method.id,
    ),
    PaymentOperationFactory(
        type=OperationTypeEnum.after_pay,
        status=OperationStatusEnum.started,
        payment_method_id=db_payment_method.id,
    ),
    PaymentOperationFactory(
        type=OperationTypeEnum.after_pay,
        status=OperationStatusEnum.completed,
        payment_method_id=db_payment_method.id,
    ),

    # when Confirming
    payment_method_repository = fake_payment_method_repository(db_payment_methods=[db_payment_method])
    result = domain.PaymentFlow(
        repository=payment_method_repository,
        operations_repository=fake_payment_operation_repository(),
        initialize_block=fake_block(
            fake_response_status=OperationStatusEnum.completed,
            fake_response_actions=[],
        ),
        process_actions_block=fake_process_actions_block(),
        pay_blocks=[],
        after_pay_blocks=[],
        confirm_blocks=[fake_block(fake_response_status=payment_operation_status)],
    ).confirm(db_payment_method.to_domain())

    # then the payment flow returns the correct Operation Response
    assert models.PaymentOperation.objects.count() == 8
    db_payment_operations = models.PaymentOperation.objects.order_by("created_at").all()
    assert db_payment_operations[0].type == OperationTypeEnum.initialize
    assert db_payment_operations[0].status == OperationStatusEnum.started

    assert db_payment_operations[1].type == OperationTypeEnum.initialize
    assert db_payment_operations[1].status == OperationStatusEnum.completed

    assert db_payment_operations[2].type == OperationTypeEnum.pay
    assert db_payment_operations[2].status == OperationStatusEnum.started

    assert db_payment_operations[3].type == OperationTypeEnum.pay
    assert db_payment_operations[3].status == OperationStatusEnum.completed

    assert db_payment_operations[4].type == OperationTypeEnum.after_pay
    assert db_payment_operations[4].status == OperationStatusEnum.started

    assert db_payment_operations[5].type == OperationTypeEnum.after_pay
    assert db_payment_operations[5].status == OperationStatusEnum.completed

    assert db_payment_operations[6].type == OperationTypeEnum.confirm
    assert db_payment_operations[6].status == OperationStatusEnum.started

    assert db_payment_operations[7].type == OperationTypeEnum.confirm
    assert db_payment_operations[7].status == result_status

    assert result.type == OperationTypeEnum.confirm
    assert result.status == result_status
    assert result.actions == []
    assert result.payment_method.id == db_payment_method.id


@pytest.mark.django_db
def test_givenAPaymentMethodThatCannotConfirm_whenConfirming_thenPaymentFlowReturnsAFailedStatusOperationResponse(
    fake_payment_method_repository,
    fake_payment_operation_repository,
    fake_block,
    fake_process_actions_block,
):
    # Given a payment method that cannot initialize
    db_payment_attempt = PaymentAttemptFactory.create()
    db_payment_method = PaymentMethodFactory.create(
        payment_attempt_id=db_payment_attempt.id,
        confirmable=False,
    )
    assert dl.can_confirm(db_payment_method.to_domain()) is False

    # When Initializing
    payment_method_repository = fake_payment_method_repository(db_payment_methods=[db_payment_method])
    result = domain.PaymentFlow(
        repository=payment_method_repository,
        operations_repository=fake_payment_operation_repository(),
        initialize_block=fake_block(),
        process_actions_block=fake_process_actions_block(),
        pay_blocks=[],
        after_pay_blocks=[],
        confirm_blocks=[fake_block()],
    ).confirm(db_payment_method.to_domain())

    # then the payment flow returns a failed status operation response
    assert result.type == OperationTypeEnum.confirm
    assert result.status == OperationStatusEnum.failed
    result.error_message == "PaymentMethod cannot go through this operation"


@pytest.mark.django_db
def test_givenANonExistingPaymentMethod_whenConfirming_thenPaymentFlowReturnsAFailedStatusOperationResponse(
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
        confirmable=False,
    )

    # When Confirming
    payment_method_repository = fake_payment_method_repository()
    result = domain.PaymentFlow(
        repository=payment_method_repository,
        operations_repository=fake_payment_operation_repository(),
        initialize_block=fake_block(),
        process_actions_block=fake_process_actions_block(),
        pay_blocks=[],
        after_pay_blocks=[],
        confirm_blocks=[],
    ).confirm(payment_method)

    # then the payment flow returns a failed status operation response
    assert result.type == OperationTypeEnum.confirm
    assert result.status == OperationStatusEnum.failed
    result.error_message == "PaymentMethod not found"
