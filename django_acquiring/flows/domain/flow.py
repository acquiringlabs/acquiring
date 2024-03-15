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
    status: PaymentOperationStatusEnum
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
    pay_blocks: List[AbstractBlock] = field(default_factory=list)

    @payment_operation_type
    def initialize(self, payment_method: AbstractPaymentMethod) -> AbstractOperationResponse:
        # Refresh the payment from the database
        try:
            payment_method = self.repository.get(id=payment_method.id)
        except PaymentMethod.DoesNotExist:
            return OperationResponse(
                status=PaymentOperationStatusEnum.failed,
                payment_method=None,
                error_message="PaymentMethod not found",
                payment_operation_type=PaymentOperationTypeEnum.initialize,
            )

        # Verify that the payment can go through this operation type
        if not dl.can_initialize(payment_method):
            return OperationResponse(
                status=PaymentOperationStatusEnum.failed,
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

        # Validate that status is one of the expected ones
        if block_response.status not in [
            PaymentOperationStatusEnum.completed,
            PaymentOperationStatusEnum.failed,
            PaymentOperationStatusEnum.requires_action,
        ]:
            self.operations_repository.add(
                payment_method=payment_method,
                type=PaymentOperationTypeEnum.initialize,  # TODO Refer to function name rather than explicit input in all cases
                status=PaymentOperationStatusEnum.failed,
            )
            return OperationResponse(
                status=PaymentOperationStatusEnum.failed,
                payment_method=payment_method,
                payment_operation_type=PaymentOperationTypeEnum.initialize,  # TODO Refer to function name rather than explicit input in all cases
                error_message=f"Invalid status {block_response.status}",
            )
        if block_response.status == PaymentOperationStatusEnum.requires_action and not block_response.actions:
            self.operations_repository.add(
                payment_method=payment_method,
                type=PaymentOperationTypeEnum.initialize,
                status=PaymentOperationStatusEnum.failed,
            )
            return OperationResponse(
                status=PaymentOperationStatusEnum.failed,
                payment_method=payment_method,
                payment_operation_type=PaymentOperationTypeEnum.initialize,
                error_message="Status is require actions, but no actions were provided",
            )

        # Create PaymentOperation with the outcome
        self.operations_repository.add(
            payment_method=payment_method,
            type=PaymentOperationTypeEnum.initialize,
            status=block_response.status,
        )

        # Return Response
        if block_response.status == PaymentOperationStatusEnum.completed:
            return self.__pay(payment_method)

        return OperationResponse(
            status=block_response.status,
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
                status=PaymentOperationStatusEnum.failed,
                payment_method=None,
                error_message="PaymentMethod not found",
                payment_operation_type=PaymentOperationTypeEnum.process_actions,
            )

        # Verify that the payment can go through this operation type
        if not dl.can_process_actions(payment_method):
            return OperationResponse(
                status=PaymentOperationStatusEnum.failed,
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

        # Validate that status is one of the expected ones
        if block_response.status not in [
            PaymentOperationStatusEnum.completed,
            PaymentOperationStatusEnum.failed,
        ]:
            self.operations_repository.add(
                payment_method=payment_method,
                type=PaymentOperationTypeEnum.process_actions,
                status=PaymentOperationStatusEnum.failed,
            )
            return OperationResponse(
                status=PaymentOperationStatusEnum.failed,
                payment_method=payment_method,
                payment_operation_type=PaymentOperationTypeEnum.process_actions,
                error_message=f"Invalid status {block_response.status}",
            )

        # Create PaymentOperation with the outcome
        self.operations_repository.add(
            payment_method=payment_method,
            type=PaymentOperationTypeEnum.process_actions,
            status=block_response.status,
        )

        # Return Response
        if block_response.status == PaymentOperationStatusEnum.completed:
            return self.__pay(payment_method)

        return OperationResponse(
            status=block_response.status,
            actions=block_response.actions,
            payment_method=payment_method,
            payment_operation_type=PaymentOperationTypeEnum.process_actions,
        )

    @payment_operation_type
    def __pay(self, payment_method: AbstractPaymentMethod) -> OperationResponse:
        # No need to refresh from DB

        # Verify that the payment can go through this operation type
        if not dl.can_pay(payment_method):
            return OperationResponse(
                status=PaymentOperationStatusEnum.failed,
                payment_method=None,
                error_message="PaymentMethod cannot go through this operation",
                payment_operation_type=PaymentOperationTypeEnum.pay,
            )

        # Create Started PaymentOperation
        self.operations_repository.add(
            payment_method=payment_method,
            type=PaymentOperationTypeEnum.pay,
            status=PaymentOperationStatusEnum.started,
        )

        # Run Operation Blocks
        responses = [block.run(payment_method) for block in self.pay_blocks]

        has_completed = all([response.status == PaymentOperationStatusEnum.completed for response in responses])

        is_pending = any([response.status == PaymentOperationStatusEnum.pending for response in responses])

        if has_completed:
            status = PaymentOperationStatusEnum.completed
        elif not has_completed and is_pending:
            status = PaymentOperationStatusEnum.pending
        else:
            # TODO Allow for the possibility of any block forcing the response to be failed
            status = PaymentOperationStatusEnum.failed

        self.operations_repository.add(
            payment_method=payment_method,
            type=PaymentOperationTypeEnum.pay,
            status=status,
        )

        # Return Response
        return OperationResponse(
            status=status,
            payment_method=payment_method,
            payment_operation_type=PaymentOperationTypeEnum.pay,
            error_message=", ".join(
                [response.error_message for response in responses if response.error_message is not None]
            ),
        )
