import uuid
from datetime import datetime
from typing import Callable, Optional

import pytest

from acquiring import domain, enums, protocols
from acquiring.domain import decision_logic as dl
from tests import protocols as test_protocols
from tests.domain import factories

COMPLETED_STATUS = [enums.OperationStatusEnum.COMPLETED]

PENDING_STATUS = [enums.OperationStatusEnum.PENDING]

FAILED_STATUS = [
    enums.OperationStatusEnum.REQUIRES_ACTION,
    enums.OperationStatusEnum.FAILED,
    enums.OperationStatusEnum.NOT_PERFORMED,
]


def test_statusListsAreComplete() -> None:
    assert set(COMPLETED_STATUS + PENDING_STATUS + FAILED_STATUS) == {
        status for status in enums.OperationStatusEnum if status != enums.OperationStatusEnum.STARTED
    }


@pytest.mark.parametrize(
    "result_status, operation_status",
    [(enums.OperationStatusEnum.COMPLETED, status) for status in COMPLETED_STATUS]
    + [(enums.OperationStatusEnum.PENDING, status) for status in PENDING_STATUS]
    + [(enums.OperationStatusEnum.FAILED, status) for status in FAILED_STATUS],
)
def test_givenAValidPaymentMethod_whenAfterConfirmingCompletes_thenPaymentMethodSagaReturnsTheCorrectOperationResponse(
    fake_unit_of_work: type[test_protocols.FakeUnitOfWork],
    fake_block: type[protocols.Block],
    fake_process_action_block: type[protocols.Block],
    fake_payment_attempt_repository_class: Callable[
        [Optional[list[protocols.PaymentAttempt]]],
        type[protocols.Repository],
    ],
    fake_milestone_repository_class: Callable[
        [Optional[list[protocols.Milestone]]],
        type[protocols.Repository],
    ],
    fake_payment_method_repository_class: Callable[
        [Optional[list[protocols.PaymentMethod]]],
        type[protocols.Repository],
    ],
    fake_operation_event_repository_class: Callable[
        [Optional[set[protocols.OperationEvent]]],
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
    result_status: enums.OperationStatusEnum,
    operation_status: enums.OperationStatusEnum,
) -> None:

    payment_attempt = factories.PaymentAttemptFactory()
    payment_method_id = protocols.ExistingPaymentMethodId(uuid.uuid4())
    payment_method = factories.PaymentMethodFactory(
        payment_attempt_id=payment_attempt.id,
        id=payment_method_id,
        confirmable=True,
        operation_events=[
            domain.OperationEvent(
                type=enums.OperationTypeEnum.INITIALIZE,
                status=enums.OperationStatusEnum.STARTED,
                payment_method_id=payment_method_id,
                created_at=datetime.now(),
            ),
            domain.OperationEvent(
                type=enums.OperationTypeEnum.INITIALIZE,
                status=enums.OperationStatusEnum.COMPLETED,
                payment_method_id=payment_method_id,
                created_at=datetime.now(),
            ),
            domain.OperationEvent(
                type=enums.OperationTypeEnum.PAY,
                status=enums.OperationStatusEnum.STARTED,
                payment_method_id=payment_method_id,
                created_at=datetime.now(),
            ),
            domain.OperationEvent(
                type=enums.OperationTypeEnum.PAY,
                status=enums.OperationStatusEnum.COMPLETED,
                payment_method_id=payment_method_id,
                created_at=datetime.now(),
            ),
            domain.OperationEvent(
                type=enums.OperationTypeEnum.AFTER_PAY,
                status=enums.OperationStatusEnum.STARTED,
                payment_method_id=payment_method_id,
                created_at=datetime.now(),
            ),
            domain.OperationEvent(
                type=enums.OperationTypeEnum.AFTER_PAY,
                status=enums.OperationStatusEnum.COMPLETED,
                payment_method_id=payment_method_id,
                created_at=datetime.now(),
            ),
            domain.OperationEvent(
                type=enums.OperationTypeEnum.CONFIRM,
                status=enums.OperationStatusEnum.STARTED,
                payment_method_id=payment_method_id,
                created_at=datetime.now(),
            ),
            domain.OperationEvent(
                type=enums.OperationTypeEnum.CONFIRM,
                status=enums.OperationStatusEnum.COMPLETED,
                payment_method_id=payment_method_id,
                created_at=datetime.now(),
            ),
        ],
    )

    unit_of_work = fake_unit_of_work(
        payment_attempt_repository_class=fake_payment_attempt_repository_class([]),
        milestone_repository_class=fake_milestone_repository_class([]),
        payment_method_repository_class=fake_payment_method_repository_class([payment_method]),
        operation_event_repository_class=fake_operation_event_repository_class(set(payment_method.operation_events)),
        block_event_repository_class=fake_block_event_repository_class(set()),
        transaction_repository_class=fake_transaction_repository_class(set()),
    )
    result = domain.PaymentMethodSaga(
        unit_of_work=unit_of_work,
        initialize_block=fake_block(  # type:ignore[call-arg]
            fake_response_status=enums.OperationStatusEnum.COMPLETED,
            fake_response_actions=[],
        ),
        process_action_block=fake_process_action_block(),
        pay_block=fake_block(),
        after_pay_blocks=[],
        confirm_block=None,
        after_confirm_blocks=[
            fake_block(  # type:ignore[call-arg]
                fake_response_status=operation_status,
            ),
        ],
    ).after_confirm(payment_method)

    operation_events = payment_method.operation_events
    assert len(operation_events) == 10

    assert operation_events[0].type == enums.OperationTypeEnum.INITIALIZE
    assert operation_events[0].status == enums.OperationStatusEnum.STARTED

    assert operation_events[1].type == enums.OperationTypeEnum.INITIALIZE
    assert operation_events[1].status == enums.OperationStatusEnum.COMPLETED

    assert operation_events[2].type == enums.OperationTypeEnum.PAY
    assert operation_events[2].status == enums.OperationStatusEnum.STARTED

    assert operation_events[3].type == enums.OperationTypeEnum.PAY
    assert operation_events[3].status == enums.OperationStatusEnum.COMPLETED

    assert operation_events[4].type == enums.OperationTypeEnum.AFTER_PAY
    assert operation_events[4].status == enums.OperationStatusEnum.STARTED

    assert operation_events[5].type == enums.OperationTypeEnum.AFTER_PAY
    assert operation_events[5].status == enums.OperationStatusEnum.COMPLETED

    assert operation_events[6].type == enums.OperationTypeEnum.CONFIRM
    assert operation_events[6].status == enums.OperationStatusEnum.STARTED

    assert operation_events[7].type == enums.OperationTypeEnum.CONFIRM
    assert operation_events[7].status == enums.OperationStatusEnum.COMPLETED

    assert operation_events[8].type == enums.OperationTypeEnum.AFTER_CONFIRM
    assert operation_events[8].status == enums.OperationStatusEnum.STARTED

    assert operation_events[9].type == enums.OperationTypeEnum.AFTER_CONFIRM
    assert operation_events[9].status == result_status

    assert result.type == enums.OperationTypeEnum.AFTER_CONFIRM
    assert result.status == result_status
    assert result.actions == []
    assert result.payment_method is not None
    assert result.payment_method.id == payment_method_id

    db_operation_events = unit_of_work.operation_event_units
    assert len(db_operation_events) == 10


def test_givenAPaymentMethodThatCannotAfterConfirm_whenAfterConfirming_thenPaymentMethodSagaReturnsAFailedStatusOperationResponse(
    fake_block: type[protocols.Block],
    fake_process_action_block: type[protocols.Block],
    fake_payment_attempt_repository_class: Callable[
        [Optional[list[protocols.PaymentAttempt]]],
        type[protocols.Repository],
    ],
    fake_milestone_repository_class: Callable[
        [Optional[list[protocols.Milestone]]],
        type[protocols.Repository],
    ],
    fake_payment_method_repository_class: Callable[
        [Optional[list[protocols.PaymentMethod]]],
        type[protocols.Repository],
    ],
    fake_operation_event_repository_class: Callable[
        [Optional[set[protocols.OperationEvent]]],
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

    payment_attempt = factories.PaymentAttemptFactory()
    payment_method_id = protocols.ExistingPaymentMethodId(uuid.uuid4())
    payment_method = factories.PaymentMethodFactory(
        payment_attempt_id=payment_attempt.id,
        id=payment_method_id,
        confirmable=False,
    )
    assert dl.can_after_confirm(payment_method) is False

    result = domain.PaymentMethodSaga(
        unit_of_work=fake_unit_of_work(
            payment_attempt_repository_class=fake_payment_attempt_repository_class([]),
            milestone_repository_class=fake_milestone_repository_class([]),
            payment_method_repository_class=fake_payment_method_repository_class([payment_method]),
            operation_event_repository_class=fake_operation_event_repository_class(set()),
            block_event_repository_class=fake_block_event_repository_class(set()),
            transaction_repository_class=fake_transaction_repository_class(set()),
        ),
        initialize_block=fake_block(),
        process_action_block=fake_process_action_block(),
        pay_block=fake_block(),
        after_pay_blocks=[],
        confirm_block=fake_block(),
        after_confirm_blocks=[fake_block()],
    ).after_confirm(payment_method)

    assert result.type == enums.OperationTypeEnum.AFTER_CONFIRM
    assert result.status == enums.OperationStatusEnum.FAILED
    result.error_message == "PaymentMethod cannot go through this operation"
