from dataclasses import dataclass

import django_acquiring.dispatchers.decision_logic as dl
from django_acquiring.payments.protocols import AbstractPaymentAttempt, PaymentOperationTypeEnum
from django_acquiring.payments.repositories import PaymentAttemptRepository

from .protocols import payment_operation_type


@dataclass
class SuccessfulOperationResponse:
    success = True
    payment_attempt: AbstractPaymentAttempt
    error_message = None
    payment_operation_type: PaymentOperationTypeEnum


@dataclass
class UnsuccessfulOperationResponse:
    success = False
    payment_attempt = None
    error_message: str
    payment_operation_type: PaymentOperationTypeEnum


# TODO Figure out how to replace this with OperationResponse protocol
OperationResponse = SuccessfulOperationResponse | UnsuccessfulOperationResponse


# TODO Decorate this class to ensure that all payment_operation_types are implemented as methods
class Dispatcher:
    repository: PaymentAttemptRepository = PaymentAttemptRepository()

    @payment_operation_type
    def authenticate(self, payment_attempt: AbstractPaymentAttempt) -> OperationResponse:
        # Refresh the payment from the database
        if (_payment_attempt := self.repository.get(id=payment_attempt.id)) is None:
            return UnsuccessfulOperationResponse(
                "Payment not found", payment_operation_type=PaymentOperationTypeEnum.authenticate
            )
        payment_attempt = _payment_attempt

        # Verify that the payment can go through this step
        if not dl.can_authenticate(payment_attempt):
            return UnsuccessfulOperationResponse(
                error_message="Payment cannot go through this operation",
                payment_operation_type=PaymentOperationTypeEnum.authenticate,
            )
        return SuccessfulOperationResponse(
            payment_attempt=payment_attempt, payment_operation_type=PaymentOperationTypeEnum.authenticate
        )
