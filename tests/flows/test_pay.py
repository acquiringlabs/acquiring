from typing import Type

import pytest

from django_acquiring import domain, models, repositories
from django_acquiring.protocols.enums import OperationStatusEnum, OperationTypeEnum
from django_acquiring.protocols.flows import AbstractBlock
from tests.factories import PaymentAttemptFactory, PaymentMethodFactory

COMPLETED_STATUS = [OperationStatusEnum.completed]

PENDING_STATUS = [OperationStatusEnum.pending]

FAILED_STATUS = [
    OperationStatusEnum.started,
    OperationStatusEnum.requires_action,
    OperationStatusEnum.failed,
]


def test_statusListsAreComplete() -> None:
    assert set(COMPLETED_STATUS + PENDING_STATUS + FAILED_STATUS) == set(OperationStatusEnum)


@pytest.mark.django_db
@pytest.mark.parametrize(
    "result_status, payment_operation_status",
    [(OperationStatusEnum.completed, status) for status in COMPLETED_STATUS]
    + [(OperationStatusEnum.pending, status) for status in PENDING_STATUS]
    + [(OperationStatusEnum.failed, status) for status in FAILED_STATUS],
)
def test_givenAValidPaymentMethod_whenInitializeCompletes_thenPaymentFlowCallsPayAndReturnsTheCorrectOperationResponse(
    fake_block: Type[AbstractBlock],
    fake_process_actions_block: Type[AbstractBlock],
    result_status: OperationStatusEnum,
    payment_operation_status: OperationStatusEnum,
) -> None:
    # given a valid payment attempt
    db_payment_attempt = PaymentAttemptFactory.create()
    db_payment_method = PaymentMethodFactory.create(payment_attempt_id=db_payment_attempt.id)

    # when Initializing
    result = domain.PaymentFlow(
        repository=repositories.PaymentMethodRepository(),
        operations_repository=repositories.PaymentOperationRepository(),
        initialize_block=fake_block(
            fake_response_status=OperationStatusEnum.completed,
            fake_response_actions=[],
        ),
        process_actions_block=fake_process_actions_block(),
        pay_blocks=[fake_block(fake_response_status=payment_operation_status)],
        after_pay_blocks=[],
        confirm_blocks=[],
    ).initialize(db_payment_method.to_domain())

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
    assert db_payment_operations[3].status == result_status

    assert result.type == OperationTypeEnum.pay
    assert result.status == result_status
    assert result.actions == []
    assert result.payment_method.id == db_payment_method.id
