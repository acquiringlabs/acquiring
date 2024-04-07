import uuid
from datetime import datetime
from typing import Callable, Optional, Type

from acquiring import domain, protocols
from acquiring.domain import decision_logic as dl
from acquiring.enums import OperationStatusEnum, OperationTypeEnum
from tests.domain import factories


def test_givenAValidPaymentMethod_whenProcessingActionsFailed_thenPaymentFlowReturnsTheCorrectOperationResponse(
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
        confirmable=True,
        payment_operations=[
            domain.PaymentOperation(
                type=OperationTypeEnum.INITIALIZE,
                status=OperationStatusEnum.STARTED,
                payment_method_id=payment_method_id,
            ),
            domain.PaymentOperation(
                type=OperationTypeEnum.INITIALIZE,
                status=OperationStatusEnum.REQUIRES_ACTION,
                payment_method_id=payment_method_id,
            ),
        ],
    )

    # when Processing Actions
    result = domain.PaymentFlow(
        payment_method_repository=fake_payment_method_repository([payment_method]),
        payment_operation_repository=fake_payment_operation_repository([]),
        initialize_block=fake_block(),
        process_action_block=fake_process_action_block(  # type:ignore[call-arg]
            fake_response_status=OperationStatusEnum.FAILED
        ),
        pay_blocks=[],
        after_pay_blocks=[],
        confirm_block=None,
        after_confirm_blocks=[],
    ).process_action(payment_method, action_data={})

    # # then the payment flow returns a failed status Operation Response
    assert result.type == OperationTypeEnum.PROCESS_ACTION
    assert result.status == OperationStatusEnum.FAILED

    assert result.payment_method is not None
    assert result.payment_method.id == payment_method.id

    db_payment_operations = payment_method.payment_operations
    assert len(db_payment_operations) == 4

    assert db_payment_operations[0].type == OperationTypeEnum.INITIALIZE
    assert db_payment_operations[0].status == OperationStatusEnum.STARTED

    assert db_payment_operations[1].type == OperationTypeEnum.INITIALIZE
    assert db_payment_operations[1].status == OperationStatusEnum.REQUIRES_ACTION

    assert db_payment_operations[2].type == OperationTypeEnum.PROCESS_ACTION
    assert db_payment_operations[2].status == OperationStatusEnum.STARTED

    assert db_payment_operations[3].type == OperationTypeEnum.PROCESS_ACTION
    assert db_payment_operations[3].status == OperationStatusEnum.FAILED


def test_givenAValidPaymentMethod_whenProcessingActionsCompletes_thenPaymentFlowReturnsTheCorrectOperationResponseAndCallsPay(
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
        confirmable=True,
        payment_operations=[
            domain.PaymentOperation(
                type=OperationTypeEnum.INITIALIZE,
                status=OperationStatusEnum.STARTED,
                payment_method_id=payment_method_id,
            ),
            domain.PaymentOperation(
                type=OperationTypeEnum.INITIALIZE,
                status=OperationStatusEnum.REQUIRES_ACTION,
                payment_method_id=payment_method_id,
            ),
        ],
    )

    # when Processing Actions
    result = domain.PaymentFlow(
        payment_method_repository=fake_payment_method_repository([payment_method]),
        payment_operation_repository=fake_payment_operation_repository([]),
        initialize_block=fake_block(),
        process_action_block=fake_process_action_block(
            fake_response_status=OperationStatusEnum.COMPLETED
        ),  # type:ignore[call-arg]
        pay_blocks=[fake_block(fake_response_status=OperationStatusEnum.COMPLETED)],  # type:ignore[call-arg]
        after_pay_blocks=[],
        confirm_block=None,
        after_confirm_blocks=[],
    ).process_action(payment_method, action_data={})

    # # then the payment flow returns a failed status Operation Response
    assert result.type == OperationTypeEnum.PAY
    assert result.status == OperationStatusEnum.COMPLETED

    assert result.payment_method is not None
    assert result.payment_method.id == payment_method.id

    db_payment_operations = payment_method.payment_operations
    assert len(db_payment_operations) == 6

    assert db_payment_operations[0].type == OperationTypeEnum.INITIALIZE
    assert db_payment_operations[0].status == OperationStatusEnum.STARTED

    assert db_payment_operations[1].type == OperationTypeEnum.INITIALIZE
    assert db_payment_operations[1].status == OperationStatusEnum.REQUIRES_ACTION

    assert db_payment_operations[2].type == OperationTypeEnum.PROCESS_ACTION
    assert db_payment_operations[2].status == OperationStatusEnum.STARTED

    assert db_payment_operations[3].type == OperationTypeEnum.PROCESS_ACTION
    assert db_payment_operations[3].status == OperationStatusEnum.COMPLETED

    assert db_payment_operations[4].type == OperationTypeEnum.PAY
    assert db_payment_operations[4].status == OperationStatusEnum.STARTED

    assert db_payment_operations[5].type == OperationTypeEnum.PAY
    assert db_payment_operations[5].status == OperationStatusEnum.COMPLETED


def test_givenAValidPaymentMethod_whenFlowDoesNotContainProcessActionBlock_thenPaymentFlowReturnsFailedOperationResponse(
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
        confirmable=True,
        payment_operations=[
            domain.PaymentOperation(
                type=OperationTypeEnum.INITIALIZE,
                status=OperationStatusEnum.STARTED,
                payment_method_id=payment_method_id,
            ),
            domain.PaymentOperation(
                type=OperationTypeEnum.INITIALIZE,
                status=OperationStatusEnum.REQUIRES_ACTION,
                payment_method_id=payment_method_id,
            ),
        ],
    )

    # when Processing Actions
    result = domain.PaymentFlow(
        payment_method_repository=fake_payment_method_repository([payment_method]),
        payment_operation_repository=fake_payment_operation_repository([]),
        initialize_block=fake_block(),
        process_action_block=None,  # not present
        pay_blocks=[],
        after_pay_blocks=[],
        confirm_block=None,
        after_confirm_blocks=[],
    ).process_action(payment_method, action_data={})

    # # then the payment flow returns a failed status Operation Response
    assert result.type == OperationTypeEnum.PROCESS_ACTION
    assert result.status == OperationStatusEnum.NOT_PERFORMED

    assert result.payment_method is not None
    assert result.payment_method.id == payment_method.id

    db_payment_operations = payment_method.payment_operations
    assert len(db_payment_operations) == 4

    assert db_payment_operations[0].type == OperationTypeEnum.INITIALIZE
    assert db_payment_operations[0].status == OperationStatusEnum.STARTED

    assert db_payment_operations[1].type == OperationTypeEnum.INITIALIZE
    assert db_payment_operations[1].status == OperationStatusEnum.REQUIRES_ACTION

    assert db_payment_operations[2].type == OperationTypeEnum.PROCESS_ACTION
    assert db_payment_operations[2].status == OperationStatusEnum.STARTED

    assert db_payment_operations[3].type == OperationTypeEnum.PROCESS_ACTION
    assert db_payment_operations[3].status == OperationStatusEnum.NOT_PERFORMED


def test_givenAPaymentMethodThatCannotProcessActions_whenProcessingActions_thenPaymentFlowReturnsAFailedStatusOperationResponse(
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
        confirmable=True,
        payment_operations=[
            domain.PaymentOperation(
                type=OperationTypeEnum.INITIALIZE,
                status=OperationStatusEnum.STARTED,
                payment_method_id=payment_method_id,
            ),
        ],
    )
    assert dl.can_process_action(payment_method) is False

    # when Processing Actions
    result = domain.PaymentFlow(
        payment_method_repository=fake_payment_method_repository([payment_method]),
        payment_operation_repository=fake_payment_operation_repository([]),
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


# TODO Move this into wrapper refresh
def test_givenANonExistingPaymentMethod_whenProcessingActions_thenPaymentFlowReturnsAFailedStatusOperationResponse(
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

    # When Processing Actions
    result = domain.PaymentFlow(
        payment_method_repository=fake_payment_method_repository([]),  # does not exist
        payment_operation_repository=fake_payment_operation_repository([]),
        initialize_block=fake_block(),
        process_action_block=fake_process_action_block(),
        pay_blocks=[],
        after_pay_blocks=[],
        confirm_block=None,
        after_confirm_blocks=[],
    ).process_action(payment_method, action_data={})

    # then the payment flow returns a failed status operation response
    assert result.type == OperationTypeEnum.PROCESS_ACTION
    assert result.status == OperationStatusEnum.FAILED
    result.error_message == "PaymentMethod not found"
