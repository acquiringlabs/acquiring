from datetime import datetime
from uuid import uuid4

import pytest

from django_acquiring.flows import PaymentFlow
from django_acquiring.flows.domain import decision_logic as dl
from django_acquiring.payments.domain import PaymentMethod
from django_acquiring.payments.models import PaymentOperation as DbPaymentOperation
from django_acquiring.protocols.payments import PaymentOperationStatusEnum, PaymentOperationTypeEnum
from tests.factories import PaymentAttemptFactory, PaymentMethodFactory, PaymentOperationFactory


# TODO Enum as List
@pytest.mark.django_db
@pytest.mark.parametrize(
    "block_response_actions, payment_operations_status",
    [
        (
            [],
            PaymentOperationStatusEnum.completed,
        ),
        (
            [{"action_data": "test"}],
            PaymentOperationStatusEnum.requires_action,
        ),
        (
            [],
            PaymentOperationStatusEnum.failed,
        ),
    ],
)
def test_givenAValidPaymentMethod_whenInitializing_thenPaymentFlowReturnsTheCorrectOperationResponse(
    fake_payment_method_repository,
    fake_payment_operation_repository,
    fake_initialize_block,
    fake_process_actions_block,
    block_response_actions,
    payment_operations_status,
):
    # given a valid payment attempt
    db_payment_attempt = PaymentAttemptFactory.create()
    db_payment_method = PaymentMethodFactory.create(payment_attempt_id=db_payment_attempt.id)

    # when Initializing
    payment_method_repository = fake_payment_method_repository(db_payment_methods=[db_payment_method])
    result = PaymentFlow(
        repository=payment_method_repository,
        operations_repository=fake_payment_operation_repository(),
        initialize_block=fake_initialize_block(
            fake_response_status=payment_operations_status,
            fake_response_actions=block_response_actions,
        ),
        process_actions_block=fake_process_actions_block(),
    ).initialize(db_payment_method.to_domain())

    # then the payment flow returns the correct Operation Response
    assert result.payment_operation_type == PaymentOperationTypeEnum.initialize
    assert result.status == payment_operations_status
    assert result.actions == block_response_actions
    assert result.payment_method.id == db_payment_method.id

    assert DbPaymentOperation.objects.count() == 2
    db_payment_operations = DbPaymentOperation.objects.order_by("created_at").all()

    assert db_payment_operations[0].type == PaymentOperationTypeEnum.initialize
    assert db_payment_operations[0].status == PaymentOperationStatusEnum.started

    assert db_payment_operations[1].type == PaymentOperationTypeEnum.initialize
    assert db_payment_operations[1].status == payment_operations_status


@pytest.mark.django_db
def test_givenAPaymentMethodThatCannotInitialize_whenInitializing_thenPaymentFlowReturnsAFailedStatusOperationResponse(
    fake_payment_method_repository,
    fake_payment_operation_repository,
    fake_initialize_block,
    fake_process_actions_block,
):
    # Given a payment method that cannot initialize
    db_payment_attempt = PaymentAttemptFactory.create()
    db_payment_method = PaymentMethodFactory.create(payment_attempt_id=db_payment_attempt.id)
    PaymentOperationFactory.create(
        payment_method_id=db_payment_method.id,
        type=PaymentOperationTypeEnum.initialize,
        status=PaymentOperationStatusEnum.started,
    )
    assert dl.can_initialize(db_payment_method.to_domain()) is False

    # When Initializing
    payment_method_repository = fake_payment_method_repository(db_payment_methods=[db_payment_method])
    result = PaymentFlow(
        repository=payment_method_repository,
        operations_repository=fake_payment_operation_repository(),
        initialize_block=fake_initialize_block(),
        process_actions_block=fake_process_actions_block(),
    ).initialize(db_payment_method.to_domain())

    # then the payment flow returns a failed status operation response
    assert result.payment_operation_type == PaymentOperationTypeEnum.initialize
    assert result.status == PaymentOperationStatusEnum.failed
    result.error_message == "PaymentMethod cannot go through this operation"


@pytest.mark.django_db
def test_givenANonExistingPaymentMethod_whenInitializing_thenPaymentFlowReturnsAFailedStatusOperationResponse(
    fake_payment_method_repository,
    fake_payment_operation_repository,
    fake_initialize_block,
    fake_process_actions_block,
):
    # Given a non existing payment method
    payment_method = PaymentMethod(
        id=uuid4(),
        created_at=datetime.now(),
        payment_attempt_id=uuid4(),
    )

    # When Initializing
    payment_method_repository = fake_payment_method_repository()
    result = PaymentFlow(
        repository=payment_method_repository,
        operations_repository=fake_payment_operation_repository(),
        initialize_block=fake_initialize_block(),
        process_actions_block=fake_process_actions_block(),
    ).initialize(payment_method)

    # then the payment flow returns a failed status operation response
    assert result.payment_operation_type == PaymentOperationTypeEnum.initialize
    assert result.status == PaymentOperationStatusEnum.failed
    result.error_message == "PaymentMethod not found"
