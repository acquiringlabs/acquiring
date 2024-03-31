import uuid
from datetime import datetime
from typing import Type

import pytest

from django_acquiring import domain, models, protocols, repositories
from django_acquiring.domain import decision_logic as dl
from django_acquiring.enums import OperationStatusEnum, OperationTypeEnum
from tests.factories import PaymentAttemptFactory, PaymentMethodFactory, PaymentOperationFactory


@pytest.mark.django_db
def test_givenAValidPaymentMethod_whenProcessingActionsFailed_thenPaymentFlowReturnsTheCorrectOperationResponse(
    fake_block: Type[protocols.AbstractBlock],
    fake_process_action_block: Type[protocols.AbstractBlock],
) -> None:
    # given a valid payment attempt
    db_payment_attempt = PaymentAttemptFactory.create()
    db_payment_method = PaymentMethodFactory.create(payment_attempt_id=db_payment_attempt.id)

    PaymentOperationFactory(
        type=OperationTypeEnum.INITIALIZE,
        status=OperationStatusEnum.STARTED,
        payment_method_id=db_payment_method.id,
    ),
    PaymentOperationFactory(
        type=OperationTypeEnum.INITIALIZE,
        status=OperationStatusEnum.REQUIRES_ACTION,
        payment_method_id=db_payment_method.id,
    ),

    # when Processing Actions
    result = domain.PaymentFlow(
        payment_method_repository=repositories.PaymentMethodRepository(),
        operations_repository=repositories.PaymentOperationRepository(),
        initialize_block=fake_block(),
        process_action_block=fake_process_action_block(fake_response_status=OperationStatusEnum.FAILED),
        pay_blocks=[],
        after_pay_blocks=[],
        confirm_block=None,
        after_confirm_blocks=[],
    ).process_action(db_payment_method.to_domain(), action_data={})

    # # then the payment flow returns a failed status Operation Response
    assert result.type == OperationTypeEnum.PROCESS_ACTION
    assert result.status == OperationStatusEnum.FAILED

    assert result.payment_method is not None
    assert result.payment_method.id == db_payment_method.id

    assert models.PaymentOperation.objects.count() == 4
    db_payment_operations = models.PaymentOperation.objects.order_by("created_at").all()

    assert db_payment_operations[0].type == OperationTypeEnum.INITIALIZE
    assert db_payment_operations[0].status == OperationStatusEnum.STARTED

    assert db_payment_operations[1].type == OperationTypeEnum.INITIALIZE
    assert db_payment_operations[1].status == OperationStatusEnum.REQUIRES_ACTION

    assert db_payment_operations[2].type == OperationTypeEnum.PROCESS_ACTION
    assert db_payment_operations[2].status == OperationStatusEnum.STARTED

    assert db_payment_operations[3].type == OperationTypeEnum.PROCESS_ACTION
    assert db_payment_operations[3].status == OperationStatusEnum.FAILED


@pytest.mark.django_db
def test_givenAValidPaymentMethod_whenProcessingActionsCompletes_thenPaymentFlowReturnsTheCorrectOperationResponseAndCallsPay(
    fake_block: Type[protocols.AbstractBlock],
    fake_process_action_block: Type[protocols.AbstractBlock],
) -> None:
    # given a valid payment attempt
    db_payment_attempt = PaymentAttemptFactory.create()
    db_payment_method = PaymentMethodFactory.create(payment_attempt_id=db_payment_attempt.id)

    PaymentOperationFactory(
        type=OperationTypeEnum.INITIALIZE,
        status=OperationStatusEnum.STARTED,
        payment_method_id=db_payment_method.id,
    ),
    PaymentOperationFactory(
        type=OperationTypeEnum.INITIALIZE,
        status=OperationStatusEnum.REQUIRES_ACTION,
        payment_method_id=db_payment_method.id,
    ),

    # when Processing Actions
    result = domain.PaymentFlow(
        payment_method_repository=repositories.PaymentMethodRepository(),
        operations_repository=repositories.PaymentOperationRepository(),
        initialize_block=fake_block(),
        process_action_block=fake_process_action_block(fake_response_status=OperationStatusEnum.COMPLETED),
        pay_blocks=[fake_block(fake_response_status=OperationStatusEnum.COMPLETED)],
        after_pay_blocks=[],
        confirm_block=None,
        after_confirm_blocks=[],
    ).process_action(db_payment_method.to_domain(), action_data={})

    # # then the payment flow returns a failed status Operation Response
    assert result.type == OperationTypeEnum.PAY
    assert result.status == OperationStatusEnum.COMPLETED

    assert result.payment_method is not None
    assert result.payment_method.id == db_payment_method.id

    assert models.PaymentOperation.objects.count() == 6
    db_payment_operations = models.PaymentOperation.objects.order_by("created_at").all()

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


@pytest.mark.django_db
def test_givenAValidPaymentMethod_whenFlowDoesNotContainProcessActionBlock_thenPaymentFlowReturnsFailedOperationResponse(
    fake_block: Type[protocols.AbstractBlock],
    fake_process_action_block: Type[protocols.AbstractBlock],
) -> None:
    # given a valid payment attempt
    db_payment_attempt = PaymentAttemptFactory.create()
    db_payment_method = PaymentMethodFactory.create(payment_attempt_id=db_payment_attempt.id)

    PaymentOperationFactory(
        type=OperationTypeEnum.INITIALIZE,
        status=OperationStatusEnum.STARTED,
        payment_method_id=db_payment_method.id,
    ),
    PaymentOperationFactory(
        type=OperationTypeEnum.INITIALIZE,
        status=OperationStatusEnum.REQUIRES_ACTION,
        payment_method_id=db_payment_method.id,
    ),

    # when Processing Actions
    result = domain.PaymentFlow(
        payment_method_repository=repositories.PaymentMethodRepository(),
        operations_repository=repositories.PaymentOperationRepository(),
        initialize_block=fake_block(),
        process_action_block=None,
        pay_blocks=[],
        after_pay_blocks=[],
        confirm_block=None,
        after_confirm_blocks=[],
    ).process_action(db_payment_method.to_domain(), action_data={})

    # # then the payment flow returns a failed status Operation Response
    assert result.type == OperationTypeEnum.PROCESS_ACTION
    assert result.status == OperationStatusEnum.NOT_PERFORMED

    assert result.payment_method is not None
    assert result.payment_method.id == db_payment_method.id

    assert models.PaymentOperation.objects.count() == 4
    db_payment_operations = models.PaymentOperation.objects.order_by("created_at").all()

    assert db_payment_operations[0].type == OperationTypeEnum.INITIALIZE
    assert db_payment_operations[0].status == OperationStatusEnum.STARTED

    assert db_payment_operations[1].type == OperationTypeEnum.INITIALIZE
    assert db_payment_operations[1].status == OperationStatusEnum.REQUIRES_ACTION

    assert db_payment_operations[2].type == OperationTypeEnum.PROCESS_ACTION
    assert db_payment_operations[2].status == OperationStatusEnum.STARTED

    assert db_payment_operations[3].type == OperationTypeEnum.PROCESS_ACTION
    assert db_payment_operations[3].status == OperationStatusEnum.NOT_PERFORMED


@pytest.mark.django_db
def test_givenAPaymentMethodThatCannotProcessActions_whenProcessingActions_thenPaymentFlowReturnsAFailedStatusOperationResponse(
    fake_block: Type[protocols.AbstractBlock],
    fake_process_action_block: Type[protocols.AbstractBlock],
) -> None:
    # Given a payment method that cannot initialize
    db_payment_attempt = PaymentAttemptFactory.create()
    db_payment_method = PaymentMethodFactory.create(payment_attempt_id=db_payment_attempt.id)
    PaymentOperationFactory.create(
        payment_method_id=db_payment_method.id,
        type=OperationTypeEnum.INITIALIZE,
        status=OperationStatusEnum.STARTED,
    )
    assert dl.can_process_action(db_payment_method.to_domain()) is False

    # when Processing Actions
    result = domain.PaymentFlow(
        payment_method_repository=repositories.PaymentMethodRepository(),
        operations_repository=repositories.PaymentOperationRepository(),
        initialize_block=fake_block(),
        process_action_block=fake_process_action_block(fake_response_status=OperationStatusEnum.COMPLETED),
        pay_blocks=[],
        after_pay_blocks=[],
        confirm_block=None,
        after_confirm_blocks=[],
    ).process_action(db_payment_method.to_domain(), action_data={})

    # then the payment flow returns a failed status operation response
    assert result.type == OperationTypeEnum.PROCESS_ACTION
    assert result.status == OperationStatusEnum.FAILED
    result.error_message == "PaymentMethod cannot go through this operation"


@pytest.mark.django_db
def test_givenANonExistingPaymentMethod_whenProcessingActions_thenPaymentFlowReturnsAFailedStatusOperationResponse(
    fake_block: Type[protocols.AbstractBlock],
    fake_process_action_block: Type[protocols.AbstractBlock],
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
        payment_method_repository=repositories.PaymentMethodRepository(),
        operations_repository=repositories.PaymentOperationRepository(),
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
