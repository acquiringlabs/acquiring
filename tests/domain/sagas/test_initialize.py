import uuid
from datetime import datetime
from typing import Callable, Optional

import pytest

from acquiring import domain, enums, protocols
from acquiring.domain import decision_logic as dl
from tests import protocols as test_protocols
from tests.domain import factories

VALID_RESPONSE_STATUS = [
    enums.OperationStatusEnum.COMPLETED,
    enums.OperationStatusEnum.FAILED,
    enums.OperationStatusEnum.REQUIRES_ACTION,
]


@pytest.mark.parametrize(
    "block_response_actions, payment_operations_status",
    [
        (
            [{"action_data": "test"}],
            enums.OperationStatusEnum.REQUIRES_ACTION,
        ),
    ]
    + [
        ([], status)
        for status in enums.OperationStatusEnum
        if status
        not in [
            enums.OperationStatusEnum.REQUIRES_ACTION,
            enums.OperationStatusEnum.NOT_PERFORMED,
            enums.OperationStatusEnum.COMPLETED,
        ]
    ],
)
def test_givenAValidPaymentMethod_whenInitializingReturns_thenPaymentSagaReturnsTheCorrectOperationResponse(
    fake_block: type[protocols.Block],
    fake_process_action_block: type[protocols.Block],
    fake_payment_attempt_repository_class: Callable[
        [Optional[list[protocols.PaymentAttempt]]],
        type[protocols.Repository],
    ],
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
    block_response_actions: list[dict],
    payment_operations_status: enums.OperationStatusEnum,
    fake_unit_of_work: type[test_protocols.FakeUnitOfWork],
) -> None:

    payment_attempt = factories.PaymentAttemptFactory()
    payment_method_id = uuid.uuid4()
    payment_method = factories.PaymentMethodFactory(
        payment_attempt_id=payment_attempt.id,
        id=payment_method_id,
    )

    unit_of_work = fake_unit_of_work(
        payment_attempt_repository_class=fake_payment_attempt_repository_class([]),
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
            fake_response_status=payment_operations_status,
            fake_response_actions=block_response_actions,
        ),
        process_action_block=fake_process_action_block(),
        pay_block=fake_block(),
        after_pay_blocks=[],
        confirm_block=None,
        after_confirm_blocks=[],
    ).initialize(payment_method)

    payment_operations = payment_method.payment_operations
    assert len(payment_operations) == 2

    assert payment_operations[0].type == enums.OperationTypeEnum.INITIALIZE
    assert payment_operations[0].status == enums.OperationStatusEnum.STARTED

    assert payment_operations[1].type == enums.OperationTypeEnum.INITIALIZE
    assert payment_operations[1].status == (
        payment_operations_status
        if payment_operations_status in VALID_RESPONSE_STATUS
        else enums.OperationStatusEnum.FAILED
    )

    payment_operations = unit_of_work.payment_operation_units
    assert len(payment_operations) == 2

    assert result.type == enums.OperationTypeEnum.INITIALIZE
    assert result.status == (
        payment_operations_status
        if payment_operations_status in VALID_RESPONSE_STATUS
        else enums.OperationStatusEnum.FAILED
    )
    assert result.actions == block_response_actions
    assert result.payment_method is not None
    assert result.payment_method.id == payment_method.id


@pytest.mark.parametrize(
    "payment_operations_status",
    [
        enums.OperationStatusEnum.COMPLETED,
        enums.OperationStatusEnum.NOT_PERFORMED,
    ],
)
def test_givenAValidPaymentMethod_whenInitializingCompletes_thenPaymentSagaReturnsTheCorrectOperationResponseAndCallsPay(
    fake_block: type[protocols.Block],
    fake_process_action_block: type[protocols.Block],
    fake_payment_attempt_repository_class: Callable[
        [Optional[list[protocols.PaymentAttempt]]],
        type[protocols.Repository],
    ],
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
    payment_operations_status: enums.OperationStatusEnum,
) -> None:

    payment_attempt = factories.PaymentAttemptFactory()
    payment_method_id = uuid.uuid4()
    payment_method = factories.PaymentMethodFactory(
        payment_attempt_id=payment_attempt.id,
        id=payment_method_id,
    )

    unit_of_work = fake_unit_of_work(
        payment_attempt_repository_class=fake_payment_attempt_repository_class([]),
        payment_method_repository_class=fake_payment_method_repository_class([payment_method]),
        payment_operation_repository_class=fake_payment_operation_repository_class(
            set(payment_method.payment_operations)
        ),
        block_event_repository_class=fake_block_event_repository_class(set()),
        transaction_repository_class=fake_transaction_repository_class(set()),
    )

    result = domain.PaymentSaga(
        unit_of_work=unit_of_work,
        initialize_block=(
            fake_block(  # type:ignore[call-arg]
                fake_response_status=payment_operations_status,
                fake_response_actions=[],
            )
            if payment_operations_status is not enums.OperationStatusEnum.NOT_PERFORMED
            else None
        ),
        process_action_block=fake_process_action_block(),
        pay_block=fake_block(),
        after_pay_blocks=[],
        confirm_block=None,
        after_confirm_blocks=[],
    ).initialize(payment_method)

    payment_operations = payment_method.payment_operations
    assert len(payment_operations) == 4

    assert payment_operations[0].type == enums.OperationTypeEnum.INITIALIZE
    assert payment_operations[0].status == enums.OperationStatusEnum.STARTED

    assert payment_operations[1].type == enums.OperationTypeEnum.INITIALIZE
    assert payment_operations[1].status == payment_operations_status

    assert payment_operations[2].type == enums.OperationTypeEnum.PAY
    assert payment_operations[2].status == enums.OperationStatusEnum.STARTED

    assert payment_operations[3].type == enums.OperationTypeEnum.PAY
    assert payment_operations[3].status == enums.OperationStatusEnum.COMPLETED

    payment_operations = unit_of_work.payment_operation_units
    assert len(payment_operations) == 4

    assert result.type == enums.OperationTypeEnum.PAY
    assert result.status == enums.OperationStatusEnum.COMPLETED
    assert result.actions == []
    assert result.payment_method is not None
    assert result.payment_method.id == payment_method.id


def test_givenAPaymentMethodThatCannotInitialize_whenInitializing_thenPaymentSagaReturnsAFailedStatusOperationResponse(
    fake_block: type[protocols.Block],
    fake_process_action_block: type[protocols.Block],
    fake_payment_attempt_repository_class: Callable[
        [Optional[list[protocols.PaymentAttempt]]],
        type[protocols.Repository],
    ],
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

    payment_attempt = factories.PaymentAttemptFactory()
    payment_method_id = uuid.uuid4()
    payment_method = factories.PaymentMethodFactory(
        payment_attempt_id=payment_attempt.id,
        id=payment_method_id,
        payment_operations=[
            domain.PaymentOperation(
                type=enums.OperationTypeEnum.INITIALIZE,
                status=enums.OperationStatusEnum.STARTED,
                payment_method_id=payment_method_id,
                created_at=datetime.now(),
            ),
        ],
    )
    assert dl.can_initialize(payment_method) is False

    unit_of_work = fake_unit_of_work(
        payment_attempt_repository_class=fake_payment_attempt_repository_class([]),
        payment_method_repository_class=fake_payment_method_repository_class([payment_method]),
        payment_operation_repository_class=fake_payment_operation_repository_class(
            set(payment_method.payment_operations)
        ),
        block_event_repository_class=fake_block_event_repository_class(set()),
        transaction_repository_class=fake_transaction_repository_class(set()),
    )
    result = domain.PaymentSaga(
        unit_of_work=unit_of_work,
        initialize_block=fake_block(),
        process_action_block=fake_process_action_block(),
        pay_block=fake_block(),
        after_pay_blocks=[],
        confirm_block=None,
        after_confirm_blocks=[],
    ).initialize(payment_method)

    assert result.type == enums.OperationTypeEnum.INITIALIZE
    assert result.status == enums.OperationStatusEnum.FAILED
    result.error_message == "PaymentMethod cannot go through this operation"


def test_givenAPaymentSagaWithoutInitializeBlock_whenInitializing_thenPaymentSagaCreatesaNotPerformedStatusAndCallsPay(
    fake_block: type[protocols.Block],
    fake_process_action_block: type[protocols.Block],
    fake_payment_attempt_repository_class: Callable[
        [Optional[list[protocols.PaymentAttempt]]],
        type[protocols.Repository],
    ],
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

    payment_attempt = factories.PaymentAttemptFactory()
    payment_method_id = uuid.uuid4()
    payment_method = factories.PaymentMethodFactory(
        payment_attempt_id=payment_attempt.id,
        id=payment_method_id,
    )

    unit_of_work = fake_unit_of_work(
        payment_attempt_repository_class=fake_payment_attempt_repository_class([]),
        payment_method_repository_class=fake_payment_method_repository_class([payment_method]),
        payment_operation_repository_class=fake_payment_operation_repository_class(
            set(payment_method.payment_operations)
        ),
        block_event_repository_class=fake_block_event_repository_class(set()),
        transaction_repository_class=fake_transaction_repository_class(set()),
    )

    result = domain.PaymentSaga(
        unit_of_work=unit_of_work,
        initialize_block=None,
        process_action_block=fake_process_action_block(),
        pay_block=fake_block(),
        after_pay_blocks=[],
        confirm_block=None,
        after_confirm_blocks=[],
    ).initialize(payment_method)

    payment_operations = payment_method.payment_operations
    assert len(payment_operations) == 4

    assert payment_operations[0].type == enums.OperationTypeEnum.INITIALIZE
    assert payment_operations[0].status == enums.OperationStatusEnum.STARTED

    assert payment_operations[1].type == enums.OperationTypeEnum.INITIALIZE
    assert payment_operations[1].status == enums.OperationStatusEnum.NOT_PERFORMED

    assert payment_operations[2].type == enums.OperationTypeEnum.PAY
    assert payment_operations[2].status == enums.OperationStatusEnum.STARTED

    assert payment_operations[3].type == enums.OperationTypeEnum.PAY
    assert payment_operations[3].status == enums.OperationStatusEnum.COMPLETED

    assert result.type == enums.OperationTypeEnum.PAY
    assert result.status == enums.OperationStatusEnum.COMPLETED
    assert result.actions == []
    assert result.payment_method is not None
    assert result.payment_method.id == payment_method.id

    db_payment_operations = unit_of_work.payment_operation_units
    assert len(db_payment_operations) == 4