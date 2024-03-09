from dataclasses import dataclass, field
from typing import List

import django_acquiring.flows.domain.decision_logic as dl
from django_acquiring.flows.blocks.protocols import AbstractBlock
from django_acquiring.flows.protocols import (
    AbstractOperationResponse,
    OperationResponse,
    UnsuccessfulOperationResponse,
    payment_operation_type,
)
from django_acquiring.payments.protocols import (
    AbstractPaymentMethod,
    PaymentOperationStatusEnum,
    PaymentOperationTypeEnum,
)
from django_acquiring.payments.repositories import PaymentAttemptRepository, PaymentMethodRepository


# TODO Decorate this class to ensure that all payment_operation_types are implemented as methods
@dataclass(kw_only=True, frozen=True)
class PaymentFlow:
    attempt_repository: PaymentAttemptRepository = PaymentAttemptRepository()
    method_repository: PaymentMethodRepository = PaymentMethodRepository()

    initialize_blocks: List[AbstractBlock] = field(default_factory=list)

    @payment_operation_type
    def initialize(self, payment_method: AbstractPaymentMethod) -> AbstractOperationResponse:
        # Refresh the payment from the database
        if (_payment_method := self.method_repository.get(id=payment_method.id)) is None:
            return UnsuccessfulOperationResponse(
                error_message="PaymentMethod not found", payment_operation_type=PaymentOperationTypeEnum.initialize
            )
        payment_method = _payment_method

        # Verify that the payment can go through this operation type
        if not dl.can_initialize(payment_method):
            return UnsuccessfulOperationResponse(
                error_message="PaymentMethod cannot go through this operation",
                payment_operation_type=PaymentOperationTypeEnum.initialize,
            )
        # Create Started PaymentOperation
        self.method_repository.add_payment_operation(
            payment_method=payment_method,
            type=PaymentOperationTypeEnum.initialize,
            status=PaymentOperationStatusEnum.started,
        )

        # Run Operation Blocks
        success = True
        actions = []
        for block in self.initialize_blocks:
            block_response = block.run(payment_method=payment_method)
            success = success and block_response.success
            actions += block_response.actions

        return OperationResponse(
            success=success,
            actions=actions,
            payment_method=payment_method,
            payment_operation_type=PaymentOperationTypeEnum.initialize,
        )
