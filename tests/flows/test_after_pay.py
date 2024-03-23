from datetime import datetime
from typing import Type
from uuid import uuid4

import pytest

from django_acquiring import domain, models, repositories
from django_acquiring.domain import decision_logic as dl
from django_acquiring.enums import OperationStatusEnum, OperationTypeEnum
from django_acquiring.protocols.flows import AbstractBlock
from tests.factories import PaymentAttemptFactory, PaymentMethodFactory, PaymentOperationFactory

COMPLETED_STATUS = [OperationStatusEnum.COMPLETED]

FAILED_STATUS = [
    OperationStatusEnum.STARTED,
    OperationStatusEnum.REQUIRES_ACTION,
    OperationStatusEnum.FAILED,
    OperationStatusEnum.PENDING,
]


def test_statusListsAreComplete() -> None:
    assert set(COMPLETED_STATUS + FAILED_STATUS) == set(OperationStatusEnum)


@pytest.mark.django_db
@pytest.mark.parametrize(
    "result_status, payment_operation_status",
    [(OperationStatusEnum.COMPLETED, status) for status in COMPLETED_STATUS]
    + [(OperationStatusEnum.FAILED, status) for status in FAILED_STATUS],
)
def test_givenAValidPaymentMethod_whenAfterPaying_thenPaymentFlowReturnsTheCorrectOperationResponse(
    fake_block: Type[AbstractBlock],
    fake_process_action_block: Type[AbstractBlock],
    result_status: OperationStatusEnum,
    payment_operation_status: OperationStatusEnum,
) -> None:
    # given a valid payment attempt
    db_payment_attempt = PaymentAttemptFactory.create()
    db_payment_method = PaymentMethodFactory.create(payment_attempt_id=db_payment_attempt.id)

    PaymentOperationFactory(
        type=OperationTypeEnum.INITIALIZE,
        status=OperationStatusEnum.STARTED,
        payment_method_id=db_payment_method.id,
    ),
    PaymentOperationFactory(
        type=OperationTypeEnum.INITIALIZE,
        status=OperationStatusEnum.COMPLETED,
        payment_method_id=db_payment_method.id,
    ),
    PaymentOperationFactory(
        type=OperationTypeEnum.PAY,
        status=OperationStatusEnum.STARTED,
        payment_method_id=db_payment_method.id,
    ),
    PaymentOperationFactory(
        type=OperationTypeEnum.PAY,
        status=OperationStatusEnum.COMPLETED,
        payment_method_id=db_payment_method.id,
    ),

    # when after paying
    result = domain.PaymentFlow(
        repository=repositories.PaymentMethodRepository(),
        operations_repository=repositories.PaymentOperationRepository(),
        initialize_block=fake_block(),
        process_action_block=fake_process_action_block(),
        pay_blocks=[],
        after_pay_blocks=[fake_block(fake_response_status=payment_operation_status)],
        confirm_blocks=[],
        after_confirm_blocks=[],
    ).after_pay(db_payment_method.to_domain())

    # then the payment flow returns the correct Operation Response
    assert models.PaymentOperation.objects.count() == 6
    db_payment_operations = models.PaymentOperation.objects.order_by("created_at").all()
    assert db_payment_operations[0].type == OperationTypeEnum.INITIALIZE
    assert db_payment_operations[0].status == OperationStatusEnum.STARTED

    assert db_payment_operations[1].type == OperationTypeEnum.INITIALIZE
    assert db_payment_operations[1].status == OperationStatusEnum.COMPLETED

    assert db_payment_operations[2].type == OperationTypeEnum.PAY
    assert db_payment_operations[2].status == OperationStatusEnum.STARTED

    assert db_payment_operations[3].type == OperationTypeEnum.PAY
    assert db_payment_operations[3].status == OperationStatusEnum.COMPLETED

    assert db_payment_operations[4].type == OperationTypeEnum.AFTER_PAY
    assert db_payment_operations[4].status == OperationStatusEnum.STARTED

    assert db_payment_operations[5].type == OperationTypeEnum.AFTER_PAY
    assert db_payment_operations[5].status == result_status

    assert result.type == OperationTypeEnum.AFTER_PAY
    assert result.status == result_status
    assert result.actions == []
    assert result.payment_method.id == db_payment_method.id


@pytest.mark.django_db
def test_givenAPaymentMethodThatCannotAfterPay_whenAfterPaying_thenPaymentFlowReturnsAFailedStatusOperationResponse(
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
    assert dl.can_after_pay(db_payment_method.to_domain()) is False

    # When After Paying
    result = domain.PaymentFlow(
        repository=repositories.PaymentMethodRepository(),
        operations_repository=repositories.PaymentOperationRepository(),
        initialize_block=fake_block(),
        process_action_block=fake_process_action_block(),
        pay_blocks=[],
        after_pay_blocks=[],
        confirm_blocks=[],
        after_confirm_blocks=[],
    ).after_pay(db_payment_method.to_domain())

    # then the payment flow returns a failed status operation response
    assert result.type == OperationTypeEnum.AFTER_PAY
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

    # When After Paying
    result = domain.PaymentFlow(
        repository=repositories.PaymentMethodRepository(),
        operations_repository=repositories.PaymentOperationRepository(),
        initialize_block=fake_block(),
        process_action_block=fake_process_action_block(),
        pay_blocks=[],
        after_pay_blocks=[],
        confirm_blocks=[],
        after_confirm_blocks=[],
    ).after_pay(payment_method)

    # then the payment flow returns a failed status operation response
    assert result.type == OperationTypeEnum.AFTER_PAY
    assert result.status == OperationStatusEnum.FAILED
    result.error_message == "PaymentMethod not found"
