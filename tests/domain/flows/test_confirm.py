import uuid
from datetime import datetime
from typing import Callable, Optional

import pytest

from acquiring import domain, protocols
from acquiring.domain import decision_logic as dl
from acquiring.enums import OperationStatusEnum, OperationTypeEnum
from tests import protocols as test_protocols
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
    "result_status, operation_status",
    [(OperationStatusEnum.COMPLETED, status) for status in COMPLETED_STATUS]
    + [(OperationStatusEnum.PENDING, status) for status in PENDING_STATUS]
    + [(OperationStatusEnum.FAILED, status) for status in FAILED_STATUS],
)
def test_givenAValidPaymentMethod_whenConfirmingCompletes_thenPaymentSagaReturnsTheCorrectOperationResponse(
    fake_block: type[protocols.Block],
    fake_process_action_block: type[protocols.Block],
    fake_payment_method_repository_class: Callable[
        [Optional[list[protocols.PaymentMethod]]],
        type[protocols.Repository],
    ],
    fake_payment_operation_repository_class: Callable[
        [Optional[set[protocols.PaymentOperation]]],
        type[test_protocols.FakeRepository],
    ],
    fake_block_event_repository_class: Callable[
        [Optional[set[protocols.BlockEvent]]],
        type[test_protocols.FakeRepository],
    ],
    fake_transaction_repository_class: Callable[
        [Optional[set[protocols.Transaction]]],
        type[test_protocols.FakeRepository],
    ],
    result_status: OperationStatusEnum,
    operation_status: OperationStatusEnum,
    fake_unit_of_work: type[test_protocols.FakeUnitOfWork],
) -> None:
    # given a valid payment attempt
    payment_attempt = factories.PaymentAttemptFactory()
    payment_method_id = uuid.uuid4()
    payment_method = factories.PaymentMethodFactory(
        payment_attempt=payment_attempt,
        id=payment_method_id,
        confirmable=True,
        payment_operations=[
            domain.PaymentOperation(
                type=OperationTypeEnum.INITIALIZE,
                status=OperationStatusEnum.STARTED,
                payment_method_id=payment_method_id,
                created_at=datetime.now(),
            ),
            domain.PaymentOperation(
                type=OperationTypeEnum.INITIALIZE,
                status=OperationStatusEnum.COMPLETED,
                payment_method_id=payment_method_id,
                created_at=datetime.now(),
            ),
            domain.PaymentOperation(
                type=OperationTypeEnum.PAY,
                status=OperationStatusEnum.STARTED,
                payment_method_id=payment_method_id,
                created_at=datetime.now(),
            ),
            domain.PaymentOperation(
                type=OperationTypeEnum.PAY,
                status=OperationStatusEnum.COMPLETED,
                payment_method_id=payment_method_id,
                created_at=datetime.now(),
            ),
            domain.PaymentOperation(
                type=OperationTypeEnum.AFTER_PAY,
                status=OperationStatusEnum.STARTED,
                payment_method_id=payment_method_id,
                created_at=datetime.now(),
            ),
            domain.PaymentOperation(
                type=OperationTypeEnum.AFTER_PAY,
                status=OperationStatusEnum.COMPLETED,
                payment_method_id=payment_method_id,
                created_at=datetime.now(),
            ),
        ],
    )

    unit_of_work = fake_unit_of_work(
        payment_method_repository_class=fake_payment_method_repository_class([payment_method]),
        payment_operation_repository_class=fake_payment_operation_repository_class(
            set(payment_method.payment_operations)
        ),
        block_event_repository_class=fake_block_event_repository_class(set()),
        transaction_repository_class=fake_transaction_repository_class(set()),
    )
    result = domain.PaymentSaga(
        unit_of_work=unit_of_work,
        initialize_block=fake_block(  # type:ignore[call-arg]
            fake_response_status=OperationStatusEnum.COMPLETED,
            fake_response_actions=[],
        ),
        process_action_block=fake_process_action_block(),
        pay_blocks=[],
        after_pay_blocks=[],
        confirm_block=fake_block(fake_response_status=operation_status),  # type:ignore[call-arg]
        after_confirm_blocks=[],
    ).confirm(payment_method)

    # then the payment flow returns the correct Operation Response
    payment_operations = payment_method.payment_operations
    assert len(payment_operations) == 8

    assert payment_operations[0].type == OperationTypeEnum.INITIALIZE
    assert payment_operations[0].status == OperationStatusEnum.STARTED

    assert payment_operations[1].type == OperationTypeEnum.INITIALIZE
    assert payment_operations[1].status == OperationStatusEnum.COMPLETED

    assert payment_operations[2].type == OperationTypeEnum.PAY
    assert payment_operations[2].status == OperationStatusEnum.STARTED

    assert payment_operations[3].type == OperationTypeEnum.PAY
    assert payment_operations[3].status == OperationStatusEnum.COMPLETED

    assert payment_operations[4].type == OperationTypeEnum.AFTER_PAY
    assert payment_operations[4].status == OperationStatusEnum.STARTED

    assert payment_operations[5].type == OperationTypeEnum.AFTER_PAY
    assert payment_operations[5].status == OperationStatusEnum.COMPLETED

    assert payment_operations[6].type == OperationTypeEnum.CONFIRM
    assert payment_operations[6].status == OperationStatusEnum.STARTED

    assert payment_operations[7].type == OperationTypeEnum.CONFIRM
    assert payment_operations[7].status == result_status

    assert result.type == OperationTypeEnum.CONFIRM
    assert result.status == result_status
    assert result.actions == []
    assert result.payment_method is not None
    assert result.payment_method.id == payment_method_id

    db_payment_operations = unit_of_work.payment_operation_units
    assert len(db_payment_operations) == 8


def test_givenAPaymentMethodThatCannotConfirm_whenConfirming_thenPaymentSagaReturnsAFailedStatusOperationResponse(
    fake_block: type[protocols.Block],
    fake_process_action_block: type[protocols.Block],
    fake_payment_method_repository_class: Callable[
        [Optional[list[protocols.PaymentMethod]]],
        type[protocols.Repository],
    ],
    fake_payment_operation_repository_class: Callable[
        [Optional[set[protocols.PaymentOperation]]],
        type[test_protocols.FakeRepository],
    ],
    fake_block_event_repository_class: Callable[
        [Optional[set[protocols.BlockEvent]]],
        type[test_protocols.FakeRepository],
    ],
    fake_transaction_repository_class: Callable[
        [Optional[set[protocols.Transaction]]],
        type[test_protocols.FakeRepository],
    ],
    fake_unit_of_work: type[test_protocols.FakeUnitOfWork],
) -> None:
    # Given a payment method that cannot initialize
    payment_attempt = factories.PaymentAttemptFactory()
    payment_method_id = uuid.uuid4()
    payment_method = factories.PaymentMethodFactory(
        payment_attempt=payment_attempt, id=payment_method_id, confirmable=False
    )
    assert dl.can_confirm(payment_method) is False

    result = domain.PaymentSaga(
        unit_of_work=fake_unit_of_work(
            payment_method_repository_class=fake_payment_method_repository_class([payment_method]),
            payment_operation_repository_class=fake_payment_operation_repository_class(set()),
            block_event_repository_class=fake_block_event_repository_class(set()),
            transaction_repository_class=fake_transaction_repository_class(set()),
        ),
        initialize_block=fake_block(),
        process_action_block=fake_process_action_block(),
        pay_blocks=[],
        after_pay_blocks=[],
        confirm_block=fake_block(),
        after_confirm_blocks=[],
    ).confirm(payment_method)

    # then the payment flow returns a failed status operation response
    assert result.type == OperationTypeEnum.CONFIRM
    assert result.status == OperationStatusEnum.FAILED
    result.error_message == "PaymentMethod cannot go through this operation"
