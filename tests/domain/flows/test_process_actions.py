import uuid
from datetime import datetime
from typing import Callable, Optional

from acquiring import domain, protocols
from acquiring.domain import decision_logic as dl
from acquiring.enums import OperationStatusEnum, OperationTypeEnum
from tests import protocols as test_protocols
from tests.domain import factories


def test_givenAValidPaymentMethod_whenProcessingActionsFailed_thenPaymentSagaReturnsTheCorrectOperationResponse(
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
                status=OperationStatusEnum.REQUIRES_ACTION,
                payment_method_id=payment_method_id,
                created_at=datetime.now(),
            ),
        ],
    )

    unit_of_work = fake_unit_of_work(
        payment_method_repository_class=fake_payment_method_repository_class([payment_method]),
        payment_operation_repository_class=fake_payment_operation_repository_class(set()),
        block_event_repository_class=fake_block_event_repository_class(set()),
        transaction_repository_class=fake_transaction_repository_class(set()),
    )

    result = domain.PaymentSaga(
        unit_of_work=unit_of_work,
        initialize_block=fake_block(),
        process_action_block=fake_process_action_block(  # type:ignore[call-arg]
            fake_response_status=OperationStatusEnum.FAILED
        ),
        pay_blocks=[],
        after_pay_blocks=[],
        confirm_block=None,
        after_confirm_blocks=[],
    ).process_action(payment_method, action_data={})

    # then the payment flow returns a failed status Operation Response
    assert result.type == OperationTypeEnum.PROCESS_ACTION
    assert result.status == OperationStatusEnum.FAILED

    assert result.payment_method is not None
    assert result.payment_method.id == payment_method.id

    payment_operations = payment_method.payment_operations
    assert len(payment_operations) == 4

    assert payment_operations[0].type == OperationTypeEnum.INITIALIZE
    assert payment_operations[0].status == OperationStatusEnum.STARTED

    assert payment_operations[1].type == OperationTypeEnum.INITIALIZE
    assert payment_operations[1].status == OperationStatusEnum.REQUIRES_ACTION

    assert payment_operations[2].type == OperationTypeEnum.PROCESS_ACTION
    assert payment_operations[2].status == OperationStatusEnum.STARTED

    assert payment_operations[3].type == OperationTypeEnum.PROCESS_ACTION
    assert payment_operations[3].status == OperationStatusEnum.FAILED

    payment_operations = unit_of_work.payment_operation_units
    len(payment_operations) == 4


def test_givenAValidPaymentMethod_whenProcessingActionsCompletes_thenPaymentSagaReturnsTheCorrectOperationResponseAndCallsPay(
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
                status=OperationStatusEnum.REQUIRES_ACTION,
                payment_method_id=payment_method_id,
                created_at=datetime.now(),
            ),
        ],
    )

    unit_of_work = fake_unit_of_work(
        payment_method_repository_class=fake_payment_method_repository_class([payment_method]),
        payment_operation_repository_class=fake_payment_operation_repository_class(set()),
        block_event_repository_class=fake_block_event_repository_class(set()),
        transaction_repository_class=fake_transaction_repository_class(set()),
    )
    result = domain.PaymentSaga(
        unit_of_work=unit_of_work,
        initialize_block=fake_block(),
        process_action_block=fake_process_action_block(
            fake_response_status=OperationStatusEnum.COMPLETED
        ),  # type:ignore[call-arg]
        pay_blocks=[fake_block(fake_response_status=OperationStatusEnum.COMPLETED)],  # type:ignore[call-arg]
        after_pay_blocks=[],
        confirm_block=None,
        after_confirm_blocks=[],
    ).process_action(payment_method, action_data={})

    # then the payment flow returns a failed status Operation Response
    assert result.type == OperationTypeEnum.PAY
    assert result.status == OperationStatusEnum.COMPLETED

    assert result.payment_method is not None
    assert result.payment_method.id == payment_method.id

    payment_operations = payment_method.payment_operations
    assert len(payment_operations) == 6

    assert payment_operations[0].type == OperationTypeEnum.INITIALIZE
    assert payment_operations[0].status == OperationStatusEnum.STARTED

    assert payment_operations[1].type == OperationTypeEnum.INITIALIZE
    assert payment_operations[1].status == OperationStatusEnum.REQUIRES_ACTION

    assert payment_operations[2].type == OperationTypeEnum.PROCESS_ACTION
    assert payment_operations[2].status == OperationStatusEnum.STARTED

    assert payment_operations[3].type == OperationTypeEnum.PROCESS_ACTION
    assert payment_operations[3].status == OperationStatusEnum.COMPLETED

    assert payment_operations[4].type == OperationTypeEnum.PAY
    assert payment_operations[4].status == OperationStatusEnum.STARTED

    assert payment_operations[5].type == OperationTypeEnum.PAY
    assert payment_operations[5].status == OperationStatusEnum.COMPLETED

    payment_operations = unit_of_work.payment_operation_units
    len(payment_operations) == 4


def test_givenAValidPaymentMethod_whenSagaDoesNotContainProcessActionBlock_thenPaymentSagaReturnsFailedOperationResponse(
    fake_block: type[protocols.Block],
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
                status=OperationStatusEnum.REQUIRES_ACTION,
                payment_method_id=payment_method_id,
                created_at=datetime.now(),
            ),
        ],
    )

    unit_of_work = fake_unit_of_work(
        payment_method_repository_class=fake_payment_method_repository_class([payment_method]),
        payment_operation_repository_class=fake_payment_operation_repository_class(set()),
        block_event_repository_class=fake_block_event_repository_class(set()),
        transaction_repository_class=fake_transaction_repository_class(set()),
    )
    result = domain.PaymentSaga(
        unit_of_work=unit_of_work,
        initialize_block=fake_block(),
        process_action_block=None,  # not present
        pay_blocks=[],
        after_pay_blocks=[],
        confirm_block=None,
        after_confirm_blocks=[],
    ).process_action(payment_method, action_data={})

    # then the payment flow returns a failed status Operation Response
    assert result.type == OperationTypeEnum.PROCESS_ACTION
    assert result.status == OperationStatusEnum.NOT_PERFORMED

    assert result.payment_method is not None
    assert result.payment_method.id == payment_method.id

    payment_operations = payment_method.payment_operations
    assert len(payment_operations) == 4

    assert payment_operations[0].type == OperationTypeEnum.INITIALIZE
    assert payment_operations[0].status == OperationStatusEnum.STARTED

    assert payment_operations[1].type == OperationTypeEnum.INITIALIZE
    assert payment_operations[1].status == OperationStatusEnum.REQUIRES_ACTION

    assert payment_operations[2].type == OperationTypeEnum.PROCESS_ACTION
    assert payment_operations[2].status == OperationStatusEnum.STARTED

    assert payment_operations[3].type == OperationTypeEnum.PROCESS_ACTION
    assert payment_operations[3].status == OperationStatusEnum.NOT_PERFORMED

    payment_operations = unit_of_work.payment_operation_units
    len(payment_operations) == 4


def test_givenAPaymentMethodThatCannotProcessActions_whenProcessingActions_thenPaymentSagaReturnsAFailedStatusOperationResponse(
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
        ],
    )
    assert dl.can_process_action(payment_method) is False

    unit_of_work = fake_unit_of_work(
        payment_method_repository_class=fake_payment_method_repository_class([payment_method]),
        payment_operation_repository_class=fake_payment_operation_repository_class(set()),
        block_event_repository_class=fake_block_event_repository_class(set()),
        transaction_repository_class=fake_transaction_repository_class(set()),
    )
    result = domain.PaymentSaga(
        unit_of_work=unit_of_work,
        initialize_block=fake_block(),
        process_action_block=fake_process_action_block(
            fake_response_status=OperationStatusEnum.COMPLETED
        ),  # type:ignore[call-arg]
        pay_blocks=[],
        after_pay_blocks=[],
        confirm_block=None,
        after_confirm_blocks=[],
    ).process_action(payment_method, action_data={})

    # then the payment flow returns a failed status operation response
    assert result.type == OperationTypeEnum.PROCESS_ACTION
    assert result.status == OperationStatusEnum.FAILED
    result.error_message == "PaymentMethod cannot go through this operation"
