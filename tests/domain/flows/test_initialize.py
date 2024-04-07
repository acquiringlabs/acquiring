import uuid
from datetime import datetime
from typing import Callable, Optional, Type

import pytest

from acquiring import domain, protocols
from acquiring.domain import decision_logic as dl
from acquiring.enums import OperationStatusEnum, OperationTypeEnum
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
            OperationStatusEnum.COMPLETED,  # check test below
        ]
    ],
)
def test_givenAValidPaymentMethod_whenInitializingReturns_thenPaymentFlowReturnsTheCorrectOperationResponse(
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
    block_response_actions: list[dict],
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
    result = domain.PaymentFlow(
        payment_method_repository=fake_payment_method_repository([payment_method]),
        payment_operation_repository=fake_payment_operation_repository([]),
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
    db_payment_operations = payment_method.payment_operations
    assert len(db_payment_operations) == 2

    assert db_payment_operations[0].type == OperationTypeEnum.INITIALIZE
    assert db_payment_operations[0].status == OperationStatusEnum.STARTED

    assert db_payment_operations[1].type == OperationTypeEnum.INITIALIZE
    assert db_payment_operations[1].status == (
        payment_operations_status if payment_operations_status in VALID_RESPONSE_STATUS else OperationStatusEnum.FAILED
    )

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
def test_givenAValidPaymentMethod_whenInitializingCompletes_thenPaymentFlowReturnsTheCorrectOperationResponseAndCallsPay(
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
    result = domain.PaymentFlow(
        payment_method_repository=fake_payment_method_repository([payment_method]),
        payment_operation_repository=fake_payment_operation_repository([]),
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
    db_payment_operations = payment_method.payment_operations
    assert len(db_payment_operations) == 4

    assert db_payment_operations[0].type == OperationTypeEnum.INITIALIZE
    assert db_payment_operations[0].status == OperationStatusEnum.STARTED

    assert db_payment_operations[1].type == OperationTypeEnum.INITIALIZE
    assert db_payment_operations[1].status == payment_operations_status

    assert db_payment_operations[2].type == OperationTypeEnum.PAY
    assert db_payment_operations[2].status == OperationStatusEnum.STARTED

    assert db_payment_operations[3].type == OperationTypeEnum.PAY
    assert db_payment_operations[3].status == OperationStatusEnum.COMPLETED

    assert result.type == OperationTypeEnum.PAY
    assert result.status == OperationStatusEnum.COMPLETED
    assert result.actions == []
    assert result.payment_method is not None
    assert result.payment_method.id == payment_method.id


def test_givenAPaymentMethodThatCannotInitialize_whenInitializing_thenPaymentFlowReturnsAFailedStatusOperationResponse(
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
            ),
        ],
    )
    assert dl.can_initialize(payment_method) is False

    # When Initializing
    result = domain.PaymentFlow(
        payment_method_repository=fake_payment_method_repository([payment_method]),
        payment_operation_repository=fake_payment_operation_repository([]),
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


# TODO Move this test to wrapper refresh_payment_method
def test_givenANonExistingPaymentMethod_whenInitializing_thenPaymentFlowReturnsAFailedStatusOperationResponse(
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

    payment_attempt = domain.PaymentAttempt(
        id=uuid.uuid4(),
        created_at=datetime.now(),
        amount=10,
        currency="USD",
        payment_method_ids=[],
    )

    payment_method = domain.PaymentMethod(
        id=uuid.uuid4(),
        payment_attempt=payment_attempt,
        created_at=datetime.now(),
        confirmable=False,
    )

    # When Initializing
    result = domain.PaymentFlow(
        payment_method_repository=fake_payment_method_repository([]),  # doesn't exist
        payment_operation_repository=fake_payment_operation_repository([]),
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
    result.error_message == "PaymentMethod not found"
