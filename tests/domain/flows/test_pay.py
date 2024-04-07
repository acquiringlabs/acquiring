import uuid
from typing import Callable, Optional, Type

import pytest

from acquiring import domain, protocols
from acquiring.enums import OperationStatusEnum, OperationTypeEnum
from tests.domain import factories

COMPLETED_STATUS = [OperationStatusEnum.COMPLETED]

PENDING_STATUS = [OperationStatusEnum.PENDING]

FAILED_STATUS = [
    OperationStatusEnum.STARTED,
    OperationStatusEnum.REQUIRES_ACTION,
    OperationStatusEnum.FAILED,
    OperationStatusEnum.NOT_PERFORMED,
]


def test_statusListsAreComplete() -> None:
    assert set(COMPLETED_STATUS + PENDING_STATUS + FAILED_STATUS) == set(OperationStatusEnum)


@pytest.mark.parametrize(
    "result_status, payment_operation_status",
    [(OperationStatusEnum.COMPLETED, status) for status in COMPLETED_STATUS]
    + [(OperationStatusEnum.PENDING, status) for status in PENDING_STATUS]
    + [(OperationStatusEnum.FAILED, status) for status in FAILED_STATUS],
)
def test_givenAValidPaymentMethod_whenInitializeCompletes_thenPaymentFlowCallsPayAndReturnsTheCorrectOperationResponse(
    fake_block: Type[protocols.AbstractBlock],
    fake_process_action_block: Type[protocols.AbstractBlock],
    fake_payment_method_repository: Callable[
        [Optional[list[protocols.AbstractPaymentMethod]]],
        protocols.AbstractRepository,
    ],
    fake_payment_operation_repository: Callable[
        [Optional[list[protocols.AbstractPaymentOperation]]],
        protocols.AbstractRepository,
    ],
    result_status: OperationStatusEnum,
    payment_operation_status: OperationStatusEnum,
) -> None:
    # given a valid payment attempt
    payment_attempt = factories.PaymentAttemptFactory()
    payment_method_id = uuid.uuid4()
    payment_method = factories.PaymentMethodFactory(
        payment_attempt=payment_attempt,
        id=payment_method_id,
    )

    # when Initializing
    result = domain.PaymentFlow(
        payment_method_repository=fake_payment_method_repository([payment_method]),
        payment_operation_repository=fake_payment_operation_repository([]),
        initialize_block=fake_block(  # type:ignore[call-arg]
            fake_response_status=OperationStatusEnum.COMPLETED,
            fake_response_actions=[],
        ),
        process_action_block=fake_process_action_block(),
        pay_blocks=[
            fake_block(fake_response_status=payment_operation_status)  # type:ignore[call-arg]
        ],
        after_pay_blocks=[],
        confirm_block=None,
        after_confirm_blocks=[],
    ).initialize(payment_method)

    # then the payment flow returns the correct Operation Response
    db_payment_operations = payment_method.payment_operations
    assert len(db_payment_operations) == 4

    assert db_payment_operations[0].type == OperationTypeEnum.INITIALIZE
    assert db_payment_operations[0].status == OperationStatusEnum.STARTED

    assert db_payment_operations[1].type == OperationTypeEnum.INITIALIZE
    assert db_payment_operations[1].status == OperationStatusEnum.COMPLETED

    assert db_payment_operations[2].type == OperationTypeEnum.PAY
    assert db_payment_operations[2].status == OperationStatusEnum.STARTED

    assert db_payment_operations[3].type == OperationTypeEnum.PAY
    assert db_payment_operations[3].status == result_status

    assert result.type == OperationTypeEnum.PAY
    assert result.status == result_status
    assert result.actions == []
    assert result.payment_method is not None
    assert result.payment_method.id == payment_method.id


def test_givenAValidPaymentMethod_whenPayCompletesWithActions_thenPaymentFlowReturnsAnOperationResponseWithActions(
    fake_block: Type[protocols.AbstractBlock],
    fake_process_action_block: Type[protocols.AbstractBlock],
    fake_payment_method_repository: Callable[
        [Optional[list[protocols.AbstractPaymentMethod]]],
        protocols.AbstractRepository,
    ],
    fake_payment_operation_repository: Callable[
        [Optional[list[protocols.AbstractPaymentOperation]]],
        protocols.AbstractRepository,
    ],
) -> None:
    # given a valid payment attempt
    payment_attempt = factories.PaymentAttemptFactory()
    payment_method_id = uuid.uuid4()
    payment_method = factories.PaymentMethodFactory(
        payment_attempt=payment_attempt,
        id=payment_method_id,
    )
    action = {"test": "action"}

    # when Initializing
    result = domain.PaymentFlow(
        payment_method_repository=fake_payment_method_repository([payment_method]),
        payment_operation_repository=fake_payment_operation_repository([]),
        initialize_block=fake_block(  # type:ignore[call-arg]
            fake_response_status=OperationStatusEnum.COMPLETED,
            fake_response_actions=[],
        ),
        process_action_block=fake_process_action_block(),
        pay_blocks=[
            fake_block(  # type:ignore[call-arg]
                fake_response_status=OperationStatusEnum.PENDING,
                fake_response_actions=[action],
            )
        ],
        after_pay_blocks=[],
        confirm_block=None,
        after_confirm_blocks=[],
    ).initialize(payment_method)

    # then the payment flow returns the correct Operation Response
    db_payment_operations = payment_method.payment_operations
    assert len(db_payment_operations) == 4

    assert db_payment_operations[0].type == OperationTypeEnum.INITIALIZE
    assert db_payment_operations[0].status == OperationStatusEnum.STARTED

    assert db_payment_operations[1].type == OperationTypeEnum.INITIALIZE
    assert db_payment_operations[1].status == OperationStatusEnum.COMPLETED

    assert db_payment_operations[2].type == OperationTypeEnum.PAY
    assert db_payment_operations[2].status == OperationStatusEnum.STARTED

    assert db_payment_operations[3].type == OperationTypeEnum.PAY
    assert db_payment_operations[3].status == OperationStatusEnum.PENDING

    assert result.type == OperationTypeEnum.PAY
    assert result.status == OperationStatusEnum.PENDING
    assert result.actions == [action]
    assert result.payment_method is not None
    assert result.payment_method.id == payment_method.id
