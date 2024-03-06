import pytest

from django_acquiring.dispatchers import Dispatcher
from django_acquiring.payments.protocols import StageNameEnum
from tests.payments.factories import PaymentAttemptFactory


@pytest.mark.django_db
def test_givenAValidPaymentAttempt_whenAuthenticating_thenTheDispatcherReturnsASuccessfulStageResponse():
    # given a valid payment attempt
    payment_attempt = PaymentAttemptFactory.create()

    # when authenticating
    result = Dispatcher().authenticate(payment_attempt)

    # then the dispatcher returns a successful stage response
    assert result.stage_name == StageNameEnum.authenticate
    assert result.payment_attempt.id == payment_attempt.id
