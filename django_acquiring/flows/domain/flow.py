from dataclasses import dataclass, field
from typing import Dict, List

import django_acquiring.flows.domain.decision_logic as dl
from django_acquiring.payments.domain import PaymentMethod
from django_acquiring.protocols.flows import AbstractBlock, AbstractOperationResponse, payment_operation_type
from django_acquiring.protocols.payments import (
    AbstractPaymentMethod,
    PaymentOperationStatusEnum,
    PaymentOperationTypeEnum,
)
from django_acquiring.protocols.repositories import AbstractRepository


@dataclass(kw_only=True)
class OperationResponse:
    success: bool
    actions: List[Dict] = field(default_factory=list)
    payment_method: AbstractPaymentMethod | None
    payment_operation_type: PaymentOperationTypeEnum
    error_message: str | None = None


# TODO Decorate this class to ensure that all payment_operation_types are implemented as methods
@dataclass(kw_only=True, frozen=True)
class PaymentFlow:
    repository: AbstractRepository
    operations_repository: AbstractRepository

    initialize_blocks: List[AbstractBlock] = field(default_factory=list)

    @payment_operation_type
    def initialize(self, payment_method: AbstractPaymentMethod) -> AbstractOperationResponse:
        # Refresh the payment from the database
        try:
            payment_method = self.repository.get(id=payment_method.id)
        except PaymentMethod.DoesNotExist:
            return OperationResponse(
                success=False,
                payment_method=None,
                error_message="PaymentMethod not found",
                payment_operation_type=PaymentOperationTypeEnum.initialize,
            )

        # Verify that the payment can go through this operation type
        if not dl.can_initialize(payment_method):
            return OperationResponse(
                success=False,
                payment_method=None,
                error_message="PaymentMethod cannot go through this operation",
                payment_operation_type=PaymentOperationTypeEnum.initialize,
            )

        # Create Started PaymentOperation
        self.operations_repository.add(
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

        # Return Response
        return OperationResponse(
            success=success,
            actions=actions,
            payment_method=payment_method,
            payment_operation_type=PaymentOperationTypeEnum.initialize,
        )
