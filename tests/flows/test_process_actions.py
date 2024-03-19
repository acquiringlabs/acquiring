from datetime import datetime
from uuid import uuid4

import pytest

from django_acquiring.flows.domain import PaymentFlow
from django_acquiring.flows.domain import decision_logic as dl
from django_acquiring.payments import domain, models
from django_acquiring.protocols.payments import OperationStatusEnum, OperationTypeEnum
from tests.factories import PaymentAttemptFactory, PaymentMethodFactory, PaymentOperationFactory


@pytest.mark.django_db
def test_givenAValidPaymentMethod_whenProcessingActionsFailed_thenPaymentFlowReturnsTheCorrectOperationResponse(
    fake_payment_method_repository,
    fake_payment_operation_repository,
    fake_block,
    fake_process_actions_block,
):
    # given a valid payment attempt
    db_payment_attempt = PaymentAttemptFactory.create()
    db_payment_method = PaymentMethodFactory.create(payment_attempt_id=db_payment_attempt.id)

    PaymentOperationFactory(
        type=OperationTypeEnum.initialize,
        status=OperationStatusEnum.started,
        payment_method_id=db_payment_method.id,
    ),
    PaymentOperationFactory(
        type=OperationTypeEnum.initialize,
        status=OperationStatusEnum.requires_action,
        payment_method_id=db_payment_method.id,
    ),

    # when Processing Actions
    payment_method_repository = fake_payment_method_repository(db_payment_methods=[db_payment_method])
    result = PaymentFlow(
        repository=payment_method_repository,
        operations_repository=fake_payment_operation_repository(),
        initialize_block=fake_block(),
        process_actions_block=fake_process_actions_block(fake_response_status=OperationStatusEnum.failed),
        pay_blocks=[],
        after_pay_blocks=[],
    ).process_actions(db_payment_method.to_domain(), action_data={})

    # # then the payment flow returns a failed status Operation Response
    assert result.payment_operation_type == OperationTypeEnum.process_actions
    assert result.status == OperationStatusEnum.failed

    assert result.payment_method.id == db_payment_method.id

    assert models.PaymentOperation.objects.count() == 4
    db_payment_operations = models.PaymentOperation.objects.order_by("created_at").all()

    assert db_payment_operations[0].type == OperationTypeEnum.initialize
    assert db_payment_operations[0].status == OperationStatusEnum.started

    assert db_payment_operations[1].type == OperationTypeEnum.initialize
    assert db_payment_operations[1].status == OperationStatusEnum.requires_action

    assert db_payment_operations[2].type == OperationTypeEnum.process_actions
    assert db_payment_operations[2].status == OperationStatusEnum.started

    assert db_payment_operations[3].type == OperationTypeEnum.process_actions
    assert db_payment_operations[3].status == OperationStatusEnum.failed


@pytest.mark.django_db
def test_givenAValidPaymentMethod_whenProcessingActionsCompletes_thenPaymentFlowReturnsTheCorrectOperationResponseAndCallsPay(
    fake_payment_method_repository,
    fake_payment_operation_repository,
    fake_block,
    fake_process_actions_block,
):
    # given a valid payment attempt
    db_payment_attempt = PaymentAttemptFactory.create()
    db_payment_method = PaymentMethodFactory.create(payment_attempt_id=db_payment_attempt.id)

    PaymentOperationFactory(
        type=OperationTypeEnum.initialize,
        status=OperationStatusEnum.started,
        payment_method_id=db_payment_method.id,
    ),
    PaymentOperationFactory(
        type=OperationTypeEnum.initialize,
        status=OperationStatusEnum.requires_action,
        payment_method_id=db_payment_method.id,
    ),

    # when Processing Actions
    payment_method_repository = fake_payment_method_repository(db_payment_methods=[db_payment_method])
    result = PaymentFlow(
        repository=payment_method_repository,
        operations_repository=fake_payment_operation_repository(),
        initialize_block=fake_block(),
        process_actions_block=fake_process_actions_block(fake_response_status=OperationStatusEnum.completed),
        pay_blocks=[fake_block(fake_response_status=OperationStatusEnum.completed)],
        after_pay_blocks=[],
    ).process_actions(db_payment_method.to_domain(), action_data={})

    # # then the payment flow returns a failed status Operation Response
    assert result.payment_operation_type == OperationTypeEnum.pay
    assert result.status == OperationStatusEnum.completed

    assert result.payment_method.id == db_payment_method.id

    assert models.PaymentOperation.objects.count() == 6
    db_payment_operations = models.PaymentOperation.objects.order_by("created_at").all()

    assert db_payment_operations[0].type == OperationTypeEnum.initialize
    assert db_payment_operations[0].status == OperationStatusEnum.started

    assert db_payment_operations[1].type == OperationTypeEnum.initialize
    assert db_payment_operations[1].status == OperationStatusEnum.requires_action

    assert db_payment_operations[2].type == OperationTypeEnum.process_actions
    assert db_payment_operations[2].status == OperationStatusEnum.started

    assert db_payment_operations[3].type == OperationTypeEnum.process_actions
    assert db_payment_operations[3].status == OperationStatusEnum.completed

    assert db_payment_operations[4].type == OperationTypeEnum.pay
    assert db_payment_operations[4].status == OperationStatusEnum.started

    assert db_payment_operations[5].type == OperationTypeEnum.pay
    assert db_payment_operations[5].status == OperationStatusEnum.completed


@pytest.mark.django_db
def test_givenAPaymentMethodThatCannotProcessActions_whenProcessingActions_thenPaymentFlowReturnsAFailedStatusOperationResponse(
    fake_payment_method_repository,
    fake_payment_operation_repository,
    fake_block,
    fake_process_actions_block,
):
    # Given a payment method that cannot initialize
    db_payment_attempt = PaymentAttemptFactory.create()
    db_payment_method = PaymentMethodFactory.create(payment_attempt_id=db_payment_attempt.id)
    PaymentOperationFactory.create(
        payment_method_id=db_payment_method.id,
        type=OperationTypeEnum.initialize,
        status=OperationStatusEnum.started,
    )
    assert dl.can_process_actions(db_payment_method.to_domain()) is False

    # when Processing Actions
    payment_method_repository = fake_payment_method_repository(db_payment_methods=[db_payment_method])
    result = PaymentFlow(
        repository=payment_method_repository,
        operations_repository=fake_payment_operation_repository(),
        initialize_block=fake_block(),
        process_actions_block=fake_process_actions_block(fake_response_status=OperationStatusEnum.completed),
        pay_blocks=[],
        after_pay_blocks=[],
    ).process_actions(db_payment_method.to_domain(), action_data={})

    # then the payment flow returns a failed status operation response
    assert result.payment_operation_type == OperationTypeEnum.process_actions
    assert result.status == OperationStatusEnum.failed
    result.error_message == "PaymentMethod cannot go through this operation"


@pytest.mark.django_db
def test_givenANonExistingPaymentMethod_whenProcessingActions_thenPaymentFlowReturnsAFailedStatusOperationResponse(
    fake_payment_method_repository,
    fake_payment_operation_repository,
    fake_block,
    fake_process_actions_block,
):
    # Given a non existing payment method
    payment_method = domain.PaymentMethod(
        id=uuid4(),
        created_at=datetime.now(),
        payment_attempt_id=uuid4(),
        confirmable=False,
    )

    # When Processing Actions
    payment_method_repository = fake_payment_method_repository()
    result = PaymentFlow(
        repository=payment_method_repository,
        operations_repository=fake_payment_operation_repository(),
        initialize_block=fake_block(),
        process_actions_block=fake_process_actions_block(),
        pay_blocks=[],
        after_pay_blocks=[],
    ).process_actions(payment_method, action_data={})

    # then the payment flow returns a failed status operation response
    assert result.payment_operation_type == OperationTypeEnum.process_actions
    assert result.status == OperationStatusEnum.failed
    result.error_message == "PaymentMethod not found"
