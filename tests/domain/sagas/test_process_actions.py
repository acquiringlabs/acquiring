import uuid
from datetime import datetime
from typing import Callable, Optional

import pytest

from acquiring import domain, enums, protocols
from acquiring.domain import decision_logic as dl
from tests import protocols as test_protocols
from tests.domain import factories


def test_givenAValidPaymentMethod_whenProcessingActionsFailed_thenPaymentMethodSagaReturnsTheCorrectOperationResponse(
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
        confirmable=True,
        payment_operations=[
            domain.PaymentOperation(
                type=enums.OperationTypeEnum.INITIALIZE,
                status=enums.OperationStatusEnum.STARTED,
                payment_method_id=payment_method_id,
                created_at=datetime.now(),
            ),
            domain.PaymentOperation(
                type=enums.OperationTypeEnum.INITIALIZE,
                status=enums.OperationStatusEnum.REQUIRES_ACTION,
                payment_method_id=payment_method_id,
                created_at=datetime.now(),
            ),
        ],
    )

    unit_of_work = fake_unit_of_work(
        payment_attempt_repository_class=fake_payment_attempt_repository_class([]),
        payment_method_repository_class=fake_payment_method_repository_class([payment_method]),
        payment_operation_repository_class=fake_payment_operation_repository_class(set()),
        block_event_repository_class=fake_block_event_repository_class(set()),
        transaction_repository_class=fake_transaction_repository_class(set()),
    )

    result = domain.PaymentMethodSaga(
        unit_of_work=unit_of_work,
        initialize_block=fake_block(),
        process_action_block=fake_process_action_block(  # type:ignore[call-arg]
            fake_response_status=enums.OperationStatusEnum.FAILED
        ),
        pay_block=fake_block(),
        after_pay_blocks=[],
        confirm_block=None,
        after_confirm_blocks=[],
    ).process_action(payment_method, action_data={})

    assert result.type == enums.OperationTypeEnum.PROCESS_ACTION
    assert result.status == enums.OperationStatusEnum.FAILED

    assert result.payment_method is not None
    assert result.payment_method.id == payment_method.id

    payment_operations = payment_method.payment_operations
    assert len(payment_operations) == 4

    assert payment_operations[0].type == enums.OperationTypeEnum.INITIALIZE
    assert payment_operations[0].status == enums.OperationStatusEnum.STARTED

    assert payment_operations[1].type == enums.OperationTypeEnum.INITIALIZE
    assert payment_operations[1].status == enums.OperationStatusEnum.REQUIRES_ACTION

    assert payment_operations[2].type == enums.OperationTypeEnum.PROCESS_ACTION
    assert payment_operations[2].status == enums.OperationStatusEnum.STARTED

    assert payment_operations[3].type == enums.OperationTypeEnum.PROCESS_ACTION
    assert payment_operations[3].status == enums.OperationStatusEnum.FAILED

    payment_operations = unit_of_work.payment_operation_units
    len(payment_operations) == 4


def test_givenAValidPaymentMethod_whenProcessingActionsCompletes_thenPaymentMethodSagaReturnsTheCorrectOperationResponseAndCallsPay(
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
        confirmable=True,
        payment_operations=[
            domain.PaymentOperation(
                type=enums.OperationTypeEnum.INITIALIZE,
                status=enums.OperationStatusEnum.STARTED,
                payment_method_id=payment_method_id,
                created_at=datetime.now(),
            ),
            domain.PaymentOperation(
                type=enums.OperationTypeEnum.INITIALIZE,
                status=enums.OperationStatusEnum.REQUIRES_ACTION,
                payment_method_id=payment_method_id,
                created_at=datetime.now(),
            ),
        ],
    )

    unit_of_work = fake_unit_of_work(
        payment_attempt_repository_class=fake_payment_attempt_repository_class([]),
        payment_method_repository_class=fake_payment_method_repository_class([payment_method]),
        payment_operation_repository_class=fake_payment_operation_repository_class(set()),
        block_event_repository_class=fake_block_event_repository_class(set()),
        transaction_repository_class=fake_transaction_repository_class(set()),
    )
    result = domain.PaymentMethodSaga(
        unit_of_work=unit_of_work,
        initialize_block=fake_block(),
        process_action_block=fake_process_action_block(
            fake_response_status=enums.OperationStatusEnum.COMPLETED
        ),  # type:ignore[call-arg]
        pay_block=fake_block(fake_response_status=enums.OperationStatusEnum.COMPLETED),  # type:ignore[call-arg]
        after_pay_blocks=[],
        confirm_block=None,
        after_confirm_blocks=[],
    ).process_action(payment_method, action_data={})

    assert result.type == enums.OperationTypeEnum.PAY
    assert result.status == enums.OperationStatusEnum.COMPLETED

    assert result.payment_method is not None
    assert result.payment_method.id == payment_method.id

    payment_operations = payment_method.payment_operations
    assert len(payment_operations) == 6

    assert payment_operations[0].type == enums.OperationTypeEnum.INITIALIZE
    assert payment_operations[0].status == enums.OperationStatusEnum.STARTED

    assert payment_operations[1].type == enums.OperationTypeEnum.INITIALIZE
    assert payment_operations[1].status == enums.OperationStatusEnum.REQUIRES_ACTION

    assert payment_operations[2].type == enums.OperationTypeEnum.PROCESS_ACTION
    assert payment_operations[2].status == enums.OperationStatusEnum.STARTED

    assert payment_operations[3].type == enums.OperationTypeEnum.PROCESS_ACTION
    assert payment_operations[3].status == enums.OperationStatusEnum.COMPLETED

    assert payment_operations[4].type == enums.OperationTypeEnum.PAY
    assert payment_operations[4].status == enums.OperationStatusEnum.STARTED

    assert payment_operations[5].type == enums.OperationTypeEnum.PAY
    assert payment_operations[5].status == enums.OperationStatusEnum.COMPLETED

    payment_operations = unit_of_work.payment_operation_units
    len(payment_operations) == 4


def test_givenAValidPaymentMethod_whenSagaDoesNotContainProcessActionBlock_thenPaymentMethodSagaReturnsFailedOperationResponse(
    fake_block: type[protocols.Block],
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
        confirmable=True,
        payment_operations=[
            domain.PaymentOperation(
                type=enums.OperationTypeEnum.INITIALIZE,
                status=enums.OperationStatusEnum.STARTED,
                payment_method_id=payment_method_id,
                created_at=datetime.now(),
            ),
            domain.PaymentOperation(
                type=enums.OperationTypeEnum.INITIALIZE,
                status=enums.OperationStatusEnum.REQUIRES_ACTION,
                payment_method_id=payment_method_id,
                created_at=datetime.now(),
            ),
        ],
    )

    unit_of_work = fake_unit_of_work(
        payment_attempt_repository_class=fake_payment_attempt_repository_class([]),
        payment_method_repository_class=fake_payment_method_repository_class([payment_method]),
        payment_operation_repository_class=fake_payment_operation_repository_class(set()),
        block_event_repository_class=fake_block_event_repository_class(set()),
        transaction_repository_class=fake_transaction_repository_class(set()),
    )

    with pytest.raises(TypeError):
        domain.PaymentMethodSaga(
            unit_of_work=unit_of_work,
            initialize_block=fake_block(),
            process_action_block=None,  # not present
            pay_block=fake_block(),
            after_pay_blocks=[],
            confirm_block=None,
            after_confirm_blocks=[],
        ).process_action(payment_method, action_data={})


def test_givenAPaymentMethodThatCannotProcessActions_whenProcessingActions_thenPaymentMethodSagaReturnsAFailedStatusOperationResponse(
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
        confirmable=True,
        payment_operations=[
            domain.PaymentOperation(
                type=enums.OperationTypeEnum.INITIALIZE,
                status=enums.OperationStatusEnum.STARTED,
                payment_method_id=payment_method_id,
                created_at=datetime.now(),
            ),
        ],
    )
    assert dl.can_process_action(payment_method) is False

    unit_of_work = fake_unit_of_work(
        payment_attempt_repository_class=fake_payment_attempt_repository_class([]),
        payment_method_repository_class=fake_payment_method_repository_class([payment_method]),
        payment_operation_repository_class=fake_payment_operation_repository_class(set()),
        block_event_repository_class=fake_block_event_repository_class(set()),
        transaction_repository_class=fake_transaction_repository_class(set()),
    )
    result = domain.PaymentMethodSaga(
        unit_of_work=unit_of_work,
        initialize_block=fake_block(),
        process_action_block=fake_process_action_block(
            fake_response_status=enums.OperationStatusEnum.COMPLETED
        ),  # type:ignore[call-arg]
        pay_block=fake_block(),
        after_pay_blocks=[],
        confirm_block=None,
        after_confirm_blocks=[],
    ).process_action(payment_method, action_data={})

    assert result.type == enums.OperationTypeEnum.PROCESS_ACTION
    assert result.status == enums.OperationStatusEnum.FAILED
    result.error_message == "PaymentMethod cannot go through this operation"
