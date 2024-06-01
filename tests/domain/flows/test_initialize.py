import uuid
from datetime import datetime
from typing import Callable, Optional

import pytest

from acquiring import domain, protocols
from acquiring.domain import decision_logic as dl
from acquiring.enums import OperationStatusEnum, OperationTypeEnum
from tests import protocols as test_protocols
from tests.domain import factories

VALID_RESPONSE_STATUS = [
    OperationStatusEnum.COMPLETED,
    OperationStatusEnum.FAILED,
    OperationStatusEnum.REQUIRES_ACTION,
]


@pytest.mark.parametrize(
    "block_response_actions, payment_operations_status",
    [
        (
            [{"action_data": "test"}],
            OperationStatusEnum.REQUIRES_ACTION,
        ),
    ]
    + [
        ([], status)
        for status in OperationStatusEnum
        if status
        not in [
            OperationStatusEnum.REQUIRES_ACTION,
            OperationStatusEnum.NOT_PERFORMED,
            OperationStatusEnum.COMPLETED,
        ]
    ],
)
def test_givenAValidPaymentMethod_whenInitializingReturns_thenPaymentSagaReturnsTheCorrectOperationResponse(
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
    block_response_actions: list[dict],
    payment_operations_status: OperationStatusEnum,
    fake_unit_of_work: type[test_protocols.FakeUnitOfWork],
) -> None:
    # given a valid payment attempt
    payment_attempt = factories.PaymentAttemptFactory()
    payment_method_id = uuid.uuid4()
    payment_method = factories.PaymentMethodFactory(
        payment_attempt=payment_attempt,
        id=payment_method_id,
    )

    # when Initializing
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
            fake_response_status=payment_operations_status,
            fake_response_actions=block_response_actions,
        ),
        process_action_block=fake_process_action_block(),
        pay_blocks=[],
        after_pay_blocks=[],
        confirm_block=None,
        after_confirm_blocks=[],
    ).initialize(payment_method)

    # then the payment flow returns the correct Operation Response
    payment_operations = payment_method.payment_operations
    assert len(payment_operations) == 2

    assert payment_operations[0].type == OperationTypeEnum.INITIALIZE
    assert payment_operations[0].status == OperationStatusEnum.STARTED

    assert payment_operations[1].type == OperationTypeEnum.INITIALIZE
    assert payment_operations[1].status == (
        payment_operations_status if payment_operations_status in VALID_RESPONSE_STATUS else OperationStatusEnum.FAILED
    )

    payment_operations = unit_of_work.payment_operation_units
    assert len(payment_operations) == 2

    assert result.type == OperationTypeEnum.INITIALIZE
    assert result.status == (
        payment_operations_status if payment_operations_status in VALID_RESPONSE_STATUS else OperationStatusEnum.FAILED
    )
    assert result.actions == block_response_actions
    assert result.payment_method is not None
    assert result.payment_method.id == payment_method.id


@pytest.mark.parametrize(
    "payment_operations_status",
    [
        OperationStatusEnum.COMPLETED,
        OperationStatusEnum.NOT_PERFORMED,
    ],
)
def test_givenAValidPaymentMethod_whenInitializingCompletes_thenPaymentSagaReturnsTheCorrectOperationResponseAndCallsPay(
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
    payment_operations_status: OperationStatusEnum,
) -> None:
    # given a valid payment attempt
    payment_attempt = factories.PaymentAttemptFactory()
    payment_method_id = uuid.uuid4()
    payment_method = factories.PaymentMethodFactory(
        payment_attempt=payment_attempt,
        id=payment_method_id,
    )

    # when Initializing
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
        initialize_block=(
            fake_block(  # type:ignore[call-arg]
                fake_response_status=payment_operations_status,
                fake_response_actions=[],
            )
            if payment_operations_status is not OperationStatusEnum.NOT_PERFORMED
            else None
        ),
        process_action_block=fake_process_action_block(),
        pay_blocks=[],
        after_pay_blocks=[],
        confirm_block=None,
        after_confirm_blocks=[],
    ).initialize(payment_method)

    # then the payment flow returns the correct Operation Response
    payment_operations = payment_method.payment_operations
    assert len(payment_operations) == 4

    assert payment_operations[0].type == OperationTypeEnum.INITIALIZE
    assert payment_operations[0].status == OperationStatusEnum.STARTED

    assert payment_operations[1].type == OperationTypeEnum.INITIALIZE
    assert payment_operations[1].status == payment_operations_status

    assert payment_operations[2].type == OperationTypeEnum.PAY
    assert payment_operations[2].status == OperationStatusEnum.STARTED

    assert payment_operations[3].type == OperationTypeEnum.PAY
    assert payment_operations[3].status == OperationStatusEnum.COMPLETED

    payment_operations = unit_of_work.payment_operation_units
    assert len(payment_operations) == 4

    assert result.type == OperationTypeEnum.PAY
    assert result.status == OperationStatusEnum.COMPLETED
    assert result.actions == []
    assert result.payment_method is not None
    assert result.payment_method.id == payment_method.id


def test_givenAPaymentMethodThatCannotInitialize_whenInitializing_thenPaymentSagaReturnsAFailedStatusOperationResponse(
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
        payment_operations=[
            domain.PaymentOperation(
                type=OperationTypeEnum.INITIALIZE,
                status=OperationStatusEnum.STARTED,
                payment_method_id=payment_method_id,
                created_at=datetime.now(),
            ),
        ],
    )
    assert dl.can_initialize(payment_method) is False

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
        initialize_block=fake_block(),
        process_action_block=fake_process_action_block(),
        pay_blocks=[],
        after_pay_blocks=[],
        confirm_block=None,
        after_confirm_blocks=[],
    ).initialize(payment_method)

    # then the payment flow returns a failed status operation response
    assert result.type == OperationTypeEnum.INITIALIZE
    assert result.status == OperationStatusEnum.FAILED
    result.error_message == "PaymentMethod cannot go through this operation"
