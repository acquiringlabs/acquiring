import uuid
from datetime import datetime
from typing import Callable, Optional

import pytest

from acquiring import domain, enums, protocols
from acquiring.domain import decision_logic as dl
from tests import protocols as test_protocols
from tests.domain import factories

COMPLETED_STATUS = [enums.OperationStatusEnum.COMPLETED]

FAILED_STATUS = [
    enums.OperationStatusEnum.REQUIRES_ACTION,
    enums.OperationStatusEnum.FAILED,
    enums.OperationStatusEnum.PENDING,
    enums.OperationStatusEnum.NOT_PERFORMED,
]


def test_statusListsAreComplete() -> None:
    assert set(COMPLETED_STATUS + FAILED_STATUS) == {
        status for status in enums.OperationStatusEnum if status != enums.OperationStatusEnum.STARTED
    }


@pytest.mark.parametrize(
    "result_status, operation_status",
    [(enums.OperationStatusEnum.COMPLETED, status) for status in COMPLETED_STATUS]
    + [(enums.OperationStatusEnum.FAILED, status) for status in FAILED_STATUS],
)
def test_givenAValidPaymentMethod_whenAfterPaying_thenPaymentMethodSagaReturnsTheCorrectOperationResponse(
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
    operation_status: enums.OperationStatusEnum,
    result_status: enums.OperationStatusEnum,
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
        initialize_block=fake_block(),
        process_action_block=fake_process_action_block(),
        pay_block=fake_block(),
        after_pay_blocks=[
            fake_block(fake_response_status=operation_status)  # type:ignore[call-arg]
        ],
        confirm_block=None,
        after_confirm_blocks=[],
    ).after_pay(payment_method)

    operation_events = payment_method.operation_events
    assert len(operation_events) == 6

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
    assert operation_events[5].status == result_status

    assert result.type == enums.OperationTypeEnum.AFTER_PAY
    assert result.status == result_status
    assert result.actions == []
    assert result.payment_method is not None
    assert result.payment_method.id == payment_method.id

    db_operation_events = unit_of_work.operation_event_units
    assert len(db_operation_events) == 6


def test_givenAPaymentMethodThatCannotAfterPay_whenAfterPaying_thenPaymentMethodSagaReturnsAFailedStatusOperationResponse(
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
        confirmable=True,
        operation_events=[
            domain.OperationEvent(
                type=enums.OperationTypeEnum.INITIALIZE,
                status=enums.OperationStatusEnum.STARTED,
                payment_method_id=payment_method_id,
                created_at=datetime.now(),
            ),
        ],
    )
    assert dl.can_after_pay(payment_method) is False

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
        after_pay_blocks=[fake_block()],
        confirm_block=None,
        after_confirm_blocks=[],
    ).after_pay(payment_method)

    assert result.type == enums.OperationTypeEnum.AFTER_PAY
    assert result.status == enums.OperationStatusEnum.FAILED
    result.error_message == "PaymentMethod cannot go through this operation"
