from datetime import datetime
from uuid import uuid4

import pytest

from django_acquiring.flows.domain import PaymentFlow
from django_acquiring.flows.domain import decision_logic as dl
from django_acquiring.payments.domain import PaymentMethod
from django_acquiring.payments.models import PaymentOperation as DbPaymentOperation
from django_acquiring.protocols.payments import PaymentOperationStatusEnum, PaymentOperationTypeEnum
from tests.factories import PaymentAttemptFactory, PaymentMethodFactory, PaymentOperationFactory


@pytest.mark.django_db
@pytest.mark.parametrize(
    "block_response_success, payment_operations_status",
    [
        (True, PaymentOperationStatusEnum.completed),
        (False, PaymentOperationStatusEnum.failed),
    ],
)
def test_givenAValidPaymentMethod_whenProcessingActions_thenPaymentFlowReturnsTheCorrectOperationResponse(
    fake_payment_method_repository,
    fake_payment_operation_repository,
    fake_initialize_block,
    fake_process_actions_block,
    block_response_success,
    payment_operations_status,
):
    # given a valid payment attempt
    db_payment_attempt = PaymentAttemptFactory.create()
    db_payment_method = PaymentMethodFactory.create(payment_attempt_id=db_payment_attempt.id)

    PaymentOperationFactory(
        type=PaymentOperationTypeEnum.initialize,
        status=PaymentOperationStatusEnum.started,
        payment_method_id=db_payment_method.id,
    ),
    PaymentOperationFactory(
        type=PaymentOperationTypeEnum.initialize,
        status=PaymentOperationStatusEnum.requires_action,
        payment_method_id=db_payment_method.id,
    ),

    # when Processing Actions
    payment_method_repository = fake_payment_method_repository(db_payment_methods=[db_payment_method])
    result = PaymentFlow(
        repository=payment_method_repository,
        operations_repository=fake_payment_operation_repository(),
        initialize_block=fake_initialize_block(),
        process_actions_block=fake_process_actions_block(
            fake_response_success=block_response_success,
        ),
    ).process_actions(db_payment_method.to_domain(), action_data={})

    # # then the payment flow returns a successful Operation Response
    assert result.payment_operation_type == PaymentOperationTypeEnum.process_actions
    assert result.success is block_response_success
    assert result.payment_method.id == db_payment_method.id

    assert DbPaymentOperation.objects.count() == 4
    db_payment_operations = DbPaymentOperation.objects.order_by("created_at").all()

    assert db_payment_operations[0].type == PaymentOperationTypeEnum.initialize
    assert db_payment_operations[0].status == PaymentOperationStatusEnum.started

    assert db_payment_operations[1].type == PaymentOperationTypeEnum.initialize
    assert db_payment_operations[1].status == PaymentOperationStatusEnum.requires_action

    assert db_payment_operations[2].type == PaymentOperationTypeEnum.process_actions
    assert db_payment_operations[2].status == PaymentOperationStatusEnum.started

    assert db_payment_operations[3].type == PaymentOperationTypeEnum.process_actions
    assert db_payment_operations[3].status == payment_operations_status


@pytest.mark.django_db
def test_givenAPaymentMethodThatCannotProcessActions_whenProcessingActions_thenPaymentFlowReturnsAnUnsuccessfulOperationResponse(
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
    assert dl.can_process_actions(db_payment_method.to_domain()) is False

    # when Processing Actions
    payment_method_repository = fake_payment_method_repository(db_payment_methods=[db_payment_method])
    result = PaymentFlow(
        repository=payment_method_repository,
        operations_repository=fake_payment_operation_repository(),
        initialize_block=fake_initialize_block(),
        process_actions_block=fake_process_actions_block(
            fake_response_success=True,
        ),
    ).process_actions(db_payment_method.to_domain(), action_data={})

    # then the payment flow returns an unsuccessful operation response
    assert result.payment_operation_type == PaymentOperationTypeEnum.process_actions
    assert result.success is False
    result.error_message == "PaymentMethod cannot go through this operation"


@pytest.mark.django_db
def test_givenANonExistingPaymentMethod_whenProcessingActions_thenPaymentFlowReturnsAnUnsuccessfulOperationResponse(
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

    # When Processing Actions
    payment_method_repository = fake_payment_method_repository()
    result = PaymentFlow(
        repository=payment_method_repository,
        operations_repository=fake_payment_operation_repository(),
        initialize_block=fake_initialize_block(),
        process_actions_block=fake_process_actions_block(),
    ).process_actions(payment_method, action_data={})

    # then the payment flow returns an unsuccessful operation response
    assert result.payment_operation_type == PaymentOperationTypeEnum.process_actions
    assert result.success is False
    result.error_message == "PaymentMethod not found"
