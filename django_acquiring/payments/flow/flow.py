from dataclasses import dataclass

import django_acquiring.payments.flow.decision_logic as dl
from django_acquiring.payments.protocols import (
    AbstractPaymentMethod,
    PaymentOperationStatusEnum,
    PaymentOperationTypeEnum,
)
from django_acquiring.payments.repositories import PaymentAttemptRepository, PaymentMethodRepository

from .protocols import payment_operation_type


@dataclass
class SuccessfulOperationResponse:
    success = True
    payment_method: AbstractPaymentMethod
    error_message = None
    payment_operation_type: PaymentOperationTypeEnum


@dataclass
class UnsuccessfulOperationResponse:
    success = False
    payment_method = None
    error_message: str
    payment_operation_type: PaymentOperationTypeEnum


# TODO Figure out how to replace this with OperationResponse protocol
OperationResponse = SuccessfulOperationResponse | UnsuccessfulOperationResponse


# TODO Decorate this class to ensure that all payment_operation_types are implemented as methods
class PaymentFlow:
    attempt_repository: PaymentAttemptRepository = PaymentAttemptRepository()
    method_repository: PaymentMethodRepository = PaymentMethodRepository()

    @payment_operation_type
    def authenticate(self, payment_method: AbstractPaymentMethod) -> OperationResponse:
        # Refresh the payment from the database
        if (_payment_method := self.method_repository.get(id=payment_method.id)) is None:
            return UnsuccessfulOperationResponse(
                "PaymentMethod not found", payment_operation_type=PaymentOperationTypeEnum.authenticate
            )
        payment_method = _payment_method

        # Verify that the payment can go through this step
        if not dl.can_authenticate(payment_method):
            return UnsuccessfulOperationResponse(
                error_message="PaymentMethod cannot go through this operation",
                payment_operation_type=PaymentOperationTypeEnum.authenticate,
            )
        # Create Started PaymentOperation
        self.method_repository.add_payment_operation(
            payment_method=payment_method,
            type=PaymentOperationTypeEnum.authenticate,
            status=PaymentOperationStatusEnum.started,
        )

        return SuccessfulOperationResponse(
            payment_method=payment_method, payment_operation_type=PaymentOperationTypeEnum.authenticate
        )
