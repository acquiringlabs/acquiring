from datetime import datetime
from typing import Type
from uuid import uuid4

import pytest

from django_acquiring import domain, models, repositories
from django_acquiring.domain import decision_logic as dl
from django_acquiring.enums import OperationStatusEnum, OperationTypeEnum
from django_acquiring.protocols.flows import AbstractBlock
from tests.factories import PaymentAttemptFactory, PaymentMethodFactory, PaymentOperationFactory

VALID_RESPONSE_STATUS = [
    OperationStatusEnum.COMPLETED,
    OperationStatusEnum.FAILED,
    OperationStatusEnum.REQUIRES_ACTION,
]


@pytest.mark.django_db
@pytest.mark.parametrize(
    "block_response_actions, payment_operations_status",
    [
        (
            [{"action_data": "test"}],
            OperationStatusEnum.REQUIRES_ACTION,
        ),
    ]
    + [
        ([], status)
        for status in OperationStatusEnum
        if status
        not in [
            OperationStatusEnum.REQUIRES_ACTION,
            OperationStatusEnum.COMPLETED,  # check test below
        ]
    ],
)
def test_givenAValidPaymentMethod_whenInitializing_thenPaymentFlowReturnsTheCorrectOperationResponse(
    fake_block: Type[AbstractBlock],
    fake_process_action_block: Type[AbstractBlock],
    block_response_actions: list[dict],
    payment_operations_status: OperationStatusEnum,
) -> None:
    # given a valid payment attempt
    db_payment_attempt = PaymentAttemptFactory.create()
    db_payment_method = PaymentMethodFactory.create(payment_attempt_id=db_payment_attempt.id)

    # when Initializing
    result = domain.PaymentFlow(
        repository=repositories.PaymentMethodRepository(),
        operations_repository=repositories.PaymentOperationRepository(),
        initialize_block=fake_block(
            fake_response_status=payment_operations_status,
            fake_response_actions=block_response_actions,
        ),
        process_action_block=fake_process_action_block(),
        pay_blocks=[],
        after_pay_blocks=[],
        confirm_blocks=[],
        after_confirm_blocks=[],
    ).initialize(db_payment_method.to_domain())

    # then the payment flow returns the correct Operation Response
    db_payment_operations = models.PaymentOperation.objects.order_by("created_at").all()

    assert db_payment_operations[0].type == OperationTypeEnum.INITIALIZE
    assert db_payment_operations[0].status == OperationStatusEnum.STARTED

    assert db_payment_operations[1].type == OperationTypeEnum.INITIALIZE
    assert db_payment_operations[1].status == (
        payment_operations_status if payment_operations_status in VALID_RESPONSE_STATUS else OperationStatusEnum.FAILED
    )

    assert models.PaymentOperation.objects.count() == 2

    assert result.type == OperationTypeEnum.INITIALIZE
    assert result.status == (
        payment_operations_status if payment_operations_status in VALID_RESPONSE_STATUS else OperationStatusEnum.FAILED
    )
    assert result.actions == block_response_actions
    assert result.payment_method.id == db_payment_method.id


@pytest.mark.django_db
def test_givenAValidPaymentMethod_whenInitializingCompletes_thenPaymentFlowReturnsTheCorrectOperationResponseAndCallsPay(
    fake_block: Type[AbstractBlock],
    fake_process_action_block: Type[AbstractBlock],
) -> None:
    # given a valid payment attempt
    db_payment_attempt = PaymentAttemptFactory.create()
    db_payment_method = PaymentMethodFactory.create(payment_attempt_id=db_payment_attempt.id)

    # when Initializing
    result = domain.PaymentFlow(
        repository=repositories.PaymentMethodRepository(),
        operations_repository=repositories.PaymentOperationRepository(),
        initialize_block=fake_block(
            fake_response_status=OperationStatusEnum.COMPLETED,
            fake_response_actions=[],
        ),
        process_action_block=fake_process_action_block(),
        pay_blocks=[],
        after_pay_blocks=[],
        confirm_blocks=[],
        after_confirm_blocks=[],
    ).initialize(db_payment_method.to_domain())

    # then the payment flow returns the correct Operation Response
    assert models.PaymentOperation.objects.count() == 4
    db_payment_operations = models.PaymentOperation.objects.order_by("created_at").all()
    assert db_payment_operations[0].type == OperationTypeEnum.INITIALIZE
    assert db_payment_operations[0].status == OperationStatusEnum.STARTED

    assert db_payment_operations[1].type == OperationTypeEnum.INITIALIZE
    assert db_payment_operations[1].status == OperationStatusEnum.COMPLETED

    assert db_payment_operations[2].type == OperationTypeEnum.PAY
    assert db_payment_operations[2].status == OperationStatusEnum.STARTED

    assert db_payment_operations[3].type == OperationTypeEnum.PAY
    assert db_payment_operations[3].status == OperationStatusEnum.COMPLETED

    assert result.type == OperationTypeEnum.PAY
    assert result.status == OperationStatusEnum.COMPLETED
    assert result.actions == []
    assert result.payment_method.id == db_payment_method.id


@pytest.mark.django_db
def test_givenAPaymentMethodThatCannotInitialize_whenInitializing_thenPaymentFlowReturnsAFailedStatusOperationResponse(
    fake_block: Type[AbstractBlock],
    fake_process_action_block: Type[AbstractBlock],
) -> None:
    # Given a payment method that cannot initialize
    db_payment_attempt = PaymentAttemptFactory.create()
    db_payment_method = PaymentMethodFactory.create(payment_attempt_id=db_payment_attempt.id)
    PaymentOperationFactory.create(
        payment_method_id=db_payment_method.id,
        type=OperationTypeEnum.INITIALIZE,
        status=OperationStatusEnum.STARTED,
    )
    assert dl.can_initialize(db_payment_method.to_domain()) is False

    # When Initializing
    result = domain.PaymentFlow(
        repository=repositories.PaymentMethodRepository(),
        operations_repository=repositories.PaymentOperationRepository(),
        initialize_block=fake_block(),
        process_action_block=fake_process_action_block(),
        pay_blocks=[],
        after_pay_blocks=[],
        confirm_blocks=[],
        after_confirm_blocks=[],
    ).initialize(db_payment_method.to_domain())

    # then the payment flow returns a failed status operation response
    assert result.type == OperationTypeEnum.INITIALIZE
    assert result.status == OperationStatusEnum.FAILED
    result.error_message == "PaymentMethod cannot go through this operation"


@pytest.mark.django_db
def test_givenANonExistingPaymentMethod_whenInitializing_thenPaymentFlowReturnsAFailedStatusOperationResponse(
    fake_block: Type[AbstractBlock],
    fake_process_action_block: Type[AbstractBlock],
) -> None:
    # Given a non existing payment method
    payment_method = domain.PaymentMethod(
        id=uuid4(),
        created_at=datetime.now(),
        payment_attempt_id=uuid4(),
        confirmable=False,
    )

    # When Initializing
    result = domain.PaymentFlow(
        repository=repositories.PaymentMethodRepository(),
        operations_repository=repositories.PaymentOperationRepository(),
        initialize_block=fake_block(),
        process_action_block=fake_process_action_block(),
        pay_blocks=[],
        after_pay_blocks=[],
        confirm_blocks=[],
        after_confirm_blocks=[],
    ).initialize(payment_method)

    # then the payment flow returns a failed status operation response
    assert result.type == OperationTypeEnum.INITIALIZE
    assert result.status == OperationStatusEnum.FAILED
    result.error_message == "PaymentMethod not found"
