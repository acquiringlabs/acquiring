import pytest

from django_acquiring.payments.flow import PaymentFlow
from django_acquiring.payments.protocols import PaymentOperationTypeEnum
from tests.payments.factories import PaymentAttemptFactory, PaymentMethodFactory


@pytest.mark.django_db
def test_givenAValidPaymentMethod_whenAuthenticating_thenThePaymentFlowReturnsASuccessfulOperationResponse():
    # given a valid payment attempt
    payment_attempt = PaymentAttemptFactory.create()
    payment_method = PaymentMethodFactory.create(payment_attempt_id=payment_attempt.id)

    # when authenticating
    result = PaymentFlow().authenticate(payment_method)

    # then the payment flow returns a successful Operation Response
    assert result.payment_operation_type == PaymentOperationTypeEnum.authenticate
    assert result.success is True
    assert result.payment_method.id == payment_method.id
