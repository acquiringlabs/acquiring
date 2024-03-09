from dataclasses import field
from typing import List

import django_acquiring.payments.flow.decision_logic as dl
from django_acquiring.payments.protocols import (
    AbstractPaymentMethod,
    PaymentOperationStatusEnum,
    PaymentOperationTypeEnum,
)
from django_acquiring.payments.repositories import PaymentAttemptRepository, PaymentMethodRepository

from .blocks.protocols import AbstractBlock
from .protocols import (
    AbstractOperationResponse,
    SuccessfulOperationResponse,
    UnsuccessfulOperationResponse,
    payment_operation_type,
)


# TODO Decorate this class to ensure that all payment_operation_types are implemented as methods
class PaymentFlow:
    attempt_repository: PaymentAttemptRepository = PaymentAttemptRepository()
    method_repository: PaymentMethodRepository = PaymentMethodRepository()

    authenticate_blocks: List[AbstractBlock] = field(default_factory=list)

    @payment_operation_type
    def authenticate(self, payment_method: AbstractPaymentMethod) -> AbstractOperationResponse:
        # Refresh the payment from the database
        if (_payment_method := self.method_repository.get(id=payment_method.id)) is None:
            return UnsuccessfulOperationResponse(
                error_message="PaymentMethod not found", payment_operation_type=PaymentOperationTypeEnum.authenticate
            )
        payment_method = _payment_method

        # Verify that the payment can go through this operation type
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

        # Run Operation Blocks
        for block in self.authenticate_blocks:
            block.run(payment_method=payment_method)

        return SuccessfulOperationResponse(
            payment_method=payment_method, payment_operation_type=PaymentOperationTypeEnum.authenticate
        )
