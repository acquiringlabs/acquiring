import pytest

from django_acquiring.dispatchers import Dispatcher
from django_acquiring.payments.protocols import PaymentOperationTypeEnum
from tests.payments.factories import PaymentAttemptFactory


@pytest.mark.django_db
def test_givenAValidPaymentAttempt_whenAuthenticating_thenTheDispatcherReturnsASuccessfulOperationResponse():
    # given a valid payment attempt
    payment_attempt = PaymentAttemptFactory.create()

    # when authenticating
    result = Dispatcher().authenticate(payment_attempt)

    # then the dispatcher returns a successful Operation Response
    assert result.payment_operation_type == PaymentOperationTypeEnum.authenticate
    assert result.payment_attempt.id == payment_attempt.id
