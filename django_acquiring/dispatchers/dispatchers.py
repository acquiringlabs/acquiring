from dataclasses import dataclass

import django_acquiring.dispatchers.decision_logic as dl
from django_acquiring.payments.protocols import AbstractPaymentAttempt, StageNameEnum
from django_acquiring.payments.repositories import PaymentAttemptRepository

from .protocols import payment_type


@dataclass
class SuccessfulStageResponse:
    success = True
    payment_attempt: AbstractPaymentAttempt
    error_message = None
    stage_name: StageNameEnum


@dataclass
class UnsuccessfulStageResponse:
    success = False
    payment_attempt = None
    error_message: str
    stage_name: StageNameEnum


# TODO Figure out how to replace this with StageResponse protocol
StageResponse = SuccessfulStageResponse | UnsuccessfulStageResponse


# TODO Decorate this class to ensure that all payment_types are implemented as methods
class Dispatcher:
    repository: PaymentAttemptRepository = PaymentAttemptRepository()

    @payment_type
    def authenticate(self, payment_attempt: AbstractPaymentAttempt) -> StageResponse:
        # Refresh the payment from the database
        if (_payment_attempt := self.repository.get(id=payment_attempt.id)) is None:
            return UnsuccessfulStageResponse("Payment not found", stage_name=StageNameEnum.authenticate)
        payment_attempt = _payment_attempt

        # Verify that the payment can go through this step
        if not dl.can_authenticate(payment_attempt):
            return UnsuccessfulStageResponse(
                error_message="Payment cannot go through this stage",
                stage_name=StageNameEnum.authenticate,
            )
        return SuccessfulStageResponse(payment_attempt=payment_attempt, stage_name=StageNameEnum.authenticate)
