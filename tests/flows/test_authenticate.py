from datetime import datetime
from uuid import uuid4

import pytest

from django_acquiring.payments.domain import PaymentMethod
from django_acquiring.payments.flow import PaymentFlow
from django_acquiring.payments.protocols import PaymentOperationStatusEnum, PaymentOperationTypeEnum
from tests.payments.factories import PaymentAttemptFactory, PaymentMethodFactory, PaymentOperationFactory


@pytest.mark.django_db
def test_givenAValidPaymentMethod_whenAuthenticating_thenPaymentFlowReturnsASuccessfulOperationResponse():
    # given a valid payment attempt
    db_payment_attempt = PaymentAttemptFactory.create()
    db_payment_method = PaymentMethodFactory.create(payment_attempt_id=db_payment_attempt.id)

    # when authenticating
    result = PaymentFlow().authenticate(db_payment_method.to_domain())

    # then the payment flow returns a successful Operation Response
    assert result.payment_operation_type == PaymentOperationTypeEnum.authenticate
    assert result.success is True
    assert result.payment_method.id == db_payment_method.id


@pytest.mark.django_db
def test_givenAnAlreadyStartedPaymentMethod_whenAuthenticating_thenPaymentFlowReturnsAnUnsuccessfulOperationResponse():
    # Given an already started payment method
    db_payment_attempt = PaymentAttemptFactory.create()
    db_payment_method = PaymentMethodFactory.create(payment_attempt_id=db_payment_attempt.id)
    PaymentOperationFactory.create(
        payment_method_id=db_payment_method.id,
        type=PaymentOperationTypeEnum.authenticate,
        status=PaymentOperationStatusEnum.started,
    )

    # When Authenticating
    result = PaymentFlow().authenticate(db_payment_method.to_domain())

    # then the payment flow returns an unsuccessful operation response
    assert result.payment_operation_type == PaymentOperationTypeEnum.authenticate
    assert result.success is False
    result.error_message == "PaymentMethod cannot go through this operation"


@pytest.mark.django_db
def test_givenANonExistingPaymentMethod_whenAuthenticating_thenPaymentFlowReturnsAnUnsuccessfulOperationResponse():
    # Given a non existing payment method
    payment_method = PaymentMethod(
        id=uuid4(),
        created_at=datetime.now(),
        payment_attempt_id=uuid4(),
    )

    # When Authenticating
    result = PaymentFlow().authenticate(payment_method)

    # then the payment flow returns an unsuccessful operation response
    assert result.payment_operation_type == PaymentOperationTypeEnum.authenticate
    assert result.success is False
    result.error_message == "PaymentMethod not found"
