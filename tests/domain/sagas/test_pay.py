import uuid
from typing import Callable, Optional

import pytest

from acquiring import domain, enums, protocols
from tests import protocols as test_protocols
from tests.domain import factories

COMPLETED_STATUS = [enums.OperationStatusEnum.COMPLETED]

PENDING_STATUS = [enums.OperationStatusEnum.PENDING]

FAILED_STATUS = [
    enums.OperationStatusEnum.FAILED,
]


@pytest.mark.parametrize(
    "operation_status",
    [enums.OperationStatusEnum.COMPLETED, enums.OperationStatusEnum.PENDING, enums.OperationStatusEnum.FAILED],
)
def test_givenAValidPaymentMethod_whenInitializeCompletes_thenPaymentMethodSagaCallsPayAndReturnsTheCorrectOperationResponse(
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
) -> None:

    payment_attempt = factories.PaymentAttemptFactory()
    payment_method_id = protocols.ExistingPaymentMethodId(uuid.uuid4())
    payment_method = factories.PaymentMethodFactory(
        payment_attempt_id=payment_attempt.id,
        id=payment_method_id,
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
        pay_block=fake_block(fake_response_status=operation_status),  # type:ignore[call-arg]
        after_pay_blocks=[],
        confirm_block=None,
        after_confirm_blocks=[],
    ).initialize(payment_method)

    operation_events = payment_method.operation_events
    assert len(operation_events) == 4

    assert operation_events[0].type == enums.OperationTypeEnum.INITIALIZE
    assert operation_events[0].status == enums.OperationStatusEnum.STARTED

    assert operation_events[1].type == enums.OperationTypeEnum.INITIALIZE
    assert operation_events[1].status == enums.OperationStatusEnum.COMPLETED

    assert operation_events[2].type == enums.OperationTypeEnum.PAY
    assert operation_events[2].status == enums.OperationStatusEnum.STARTED

    assert operation_events[3].type == enums.OperationTypeEnum.PAY
    assert operation_events[3].status == operation_status

    assert result.type == enums.OperationTypeEnum.PAY
    assert result.status == operation_status
    assert result.actions == []
    assert result.payment_method is not None
    assert result.payment_method.id == payment_method.id

    db_operation_events = unit_of_work.operation_event_units
    assert len(db_operation_events) == 4
