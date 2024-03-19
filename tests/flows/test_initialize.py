from datetime import datetime
from uuid import uuid4

import pytest

from django_acquiring.flows import PaymentFlow
from django_acquiring.flows.domain import decision_logic as dl
from django_acquiring.payments import domain, models
from django_acquiring.protocols.payments import OperationStatusEnum, OperationTypeEnum
from tests.factories import PaymentAttemptFactory, PaymentMethodFactory, PaymentOperationFactory

VALID_RESPONSE_STATUS = [
    OperationStatusEnum.completed,
    OperationStatusEnum.failed,
    OperationStatusEnum.requires_action,
]


@pytest.mark.django_db
@pytest.mark.parametrize(
    "block_response_actions, payment_operations_status",
    [
        (
            [{"action_data": "test"}],
            OperationStatusEnum.requires_action,
        ),
    ]
    + [
        ([], status)
        for status in OperationStatusEnum
        if status
        not in [
            OperationStatusEnum.requires_action,
            OperationStatusEnum.completed,  # check test below
        ]
    ],
)
def test_givenAValidPaymentMethod_whenInitializing_thenPaymentFlowReturnsTheCorrectOperationResponse(
    fake_payment_method_repository,
    fake_payment_operation_repository,
    fake_block,
    fake_process_actions_block,
    block_response_actions,
    payment_operations_status,
):
    # given a valid payment attempt
    db_payment_attempt = PaymentAttemptFactory.create()
    db_payment_method = PaymentMethodFactory.create(payment_attempt_id=db_payment_attempt.id)

    # when Initializing
    payment_method_repository = fake_payment_method_repository(db_payment_methods=[db_payment_method])
    result = PaymentFlow(
        repository=payment_method_repository,
        operations_repository=fake_payment_operation_repository(),
        initialize_block=fake_block(
            fake_response_status=payment_operations_status,
            fake_response_actions=block_response_actions,
        ),
        process_actions_block=fake_process_actions_block(),
        pay_blocks=[],
        after_pay_blocks=[],
    ).initialize(db_payment_method.to_domain())

    # then the payment flow returns the correct Operation Response
    db_payment_operations = models.PaymentOperation.objects.order_by("created_at").all()

    assert db_payment_operations[0].type == OperationTypeEnum.initialize
    assert db_payment_operations[0].status == OperationStatusEnum.started

    assert db_payment_operations[1].type == OperationTypeEnum.initialize
    assert db_payment_operations[1].status == (
        payment_operations_status if payment_operations_status in VALID_RESPONSE_STATUS else OperationStatusEnum.failed
    )

    assert models.PaymentOperation.objects.count() == 2

    assert result.payment_operation_type == OperationTypeEnum.initialize
    assert result.status == (
        payment_operations_status if payment_operations_status in VALID_RESPONSE_STATUS else OperationStatusEnum.failed
    )
    assert result.actions == block_response_actions
    assert result.payment_method.id == db_payment_method.id


@pytest.mark.django_db
def test_givenAValidPaymentMethod_whenInitializingCompletes_thenPaymentFlowReturnsTheCorrectOperationResponseAndCallsPay(
    fake_payment_method_repository,
    fake_payment_operation_repository,
    fake_block,
    fake_process_actions_block,
):
    # given a valid payment attempt
    db_payment_attempt = PaymentAttemptFactory.create()
    db_payment_method = PaymentMethodFactory.create(payment_attempt_id=db_payment_attempt.id)

    # when Initializing
    payment_method_repository = fake_payment_method_repository(db_payment_methods=[db_payment_method])
    payment_flow = PaymentFlow(
        repository=payment_method_repository,
        operations_repository=fake_payment_operation_repository(),
        initialize_block=fake_block(
            fake_response_status=OperationStatusEnum.completed,
            fake_response_actions=[],
        ),
        process_actions_block=fake_process_actions_block(),
        pay_blocks=[],
        after_pay_blocks=[],
    )

    result = payment_flow.initialize(db_payment_method.to_domain())

    # then the payment flow returns the correct Operation Response
    assert models.PaymentOperation.objects.count() == 4
    db_payment_operations = models.PaymentOperation.objects.order_by("created_at").all()
    assert db_payment_operations[0].type == OperationTypeEnum.initialize
    assert db_payment_operations[0].status == OperationStatusEnum.started

    assert db_payment_operations[1].type == OperationTypeEnum.initialize
    assert db_payment_operations[1].status == OperationStatusEnum.completed

    assert db_payment_operations[2].type == OperationTypeEnum.pay
    assert db_payment_operations[2].status == OperationStatusEnum.started

    assert db_payment_operations[3].type == OperationTypeEnum.pay
    assert db_payment_operations[3].status == OperationStatusEnum.completed

    assert result.payment_operation_type == OperationTypeEnum.pay
    assert result.status == OperationStatusEnum.completed
    assert result.actions == []
    assert result.payment_method.id == db_payment_method.id


@pytest.mark.django_db
def test_givenAPaymentMethodThatCannotInitialize_whenInitializing_thenPaymentFlowReturnsAFailedStatusOperationResponse(
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
        type=OperationTypeEnum.initialize,
        status=OperationStatusEnum.started,
    )
    assert dl.can_initialize(db_payment_method.to_domain()) is False

    # When Initializing
    payment_method_repository = fake_payment_method_repository(db_payment_methods=[db_payment_method])
    result = PaymentFlow(
        repository=payment_method_repository,
        operations_repository=fake_payment_operation_repository(),
        initialize_block=fake_block(),
        process_actions_block=fake_process_actions_block(),
        pay_blocks=[],
        after_pay_blocks=[],
    ).initialize(db_payment_method.to_domain())

    # then the payment flow returns a failed status operation response
    assert result.payment_operation_type == OperationTypeEnum.initialize
    assert result.status == OperationStatusEnum.failed
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
        confirmable=False,
    )

    # When Initializing
    payment_method_repository = fake_payment_method_repository()
    result = PaymentFlow(
        repository=payment_method_repository,
        operations_repository=fake_payment_operation_repository(),
        initialize_block=fake_block(),
        process_actions_block=fake_process_actions_block(),
        pay_blocks=[],
        after_pay_blocks=[],
    ).initialize(payment_method)

    # then the payment flow returns a failed status operation response
    assert result.payment_operation_type == OperationTypeEnum.initialize
    assert result.status == OperationStatusEnum.failed
    result.error_message == "PaymentMethod not found"
