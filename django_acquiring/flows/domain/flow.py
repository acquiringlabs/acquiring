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


@dataclass
class OperationResponse:
    success: bool
    payment_method: AbstractPaymentMethod | None
    payment_operation_type: PaymentOperationTypeEnum
    error_message: str | None = None
    actions: List[Dict] = field(default_factory=list)


# TODO Decorate this class to ensure that all payment_operation_types are implemented as methods
@dataclass(frozen=True)
class PaymentFlow:
    repository: AbstractRepository
    operations_repository: AbstractRepository

    initialize_block: AbstractBlock
    process_actions_block: AbstractBlock

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

        # Run Operation Block
        block_response = self.initialize_block.run(payment_method=payment_method)

        # Create PaymentOperation with the outcome
        if block_response.success and len(block_response.actions) == 0:
            status = PaymentOperationStatusEnum.completed
        elif block_response.success and len(block_response.actions) > 0:
            status = PaymentOperationStatusEnum.requires_action
        else:
            status = PaymentOperationStatusEnum.failed

        self.operations_repository.add(
            payment_method=payment_method,
            type=PaymentOperationTypeEnum.initialize,
            status=status,
        )

        # Return Response
        return OperationResponse(
            success=block_response.success,
            actions=block_response.actions,
            payment_method=payment_method,
            payment_operation_type=PaymentOperationTypeEnum.initialize,
        )

    @payment_operation_type
    def process_actions(self, payment_method: AbstractPaymentMethod, action_data: Dict) -> AbstractOperationResponse:
        # Refresh the payment from the database
        try:
            payment_method = self.repository.get(id=payment_method.id)
        except PaymentMethod.DoesNotExist:
            return OperationResponse(
                success=False,
                payment_method=None,
                error_message="PaymentMethod not found",
                payment_operation_type=PaymentOperationTypeEnum.process_actions,
            )

        # Verify that the payment can go through this operation type
        if not dl.can_process_actions(payment_method):
            return OperationResponse(
                success=False,
                payment_method=None,
                error_message="PaymentMethod cannot go through this operation",
                payment_operation_type=PaymentOperationTypeEnum.process_actions,
            )

        # Create Started PaymentOperation
        self.operations_repository.add(
            payment_method=payment_method,
            type=PaymentOperationTypeEnum.process_actions,
            status=PaymentOperationStatusEnum.started,
        )

        # Run Operation Block
        block_response = self.process_actions_block.run(payment_method=payment_method, action_data=action_data)

        # Create PaymentOperation with the outcome
        self.operations_repository.add(
            payment_method=payment_method,
            type=PaymentOperationTypeEnum.process_actions,
            status=(
                PaymentOperationStatusEnum.completed if block_response.success else PaymentOperationStatusEnum.failed
            ),
        )

        # Return Response
        return OperationResponse(
            success=block_response.success,
            actions=block_response.actions,
            payment_method=payment_method,
            payment_operation_type=PaymentOperationTypeEnum.process_actions,
        )
