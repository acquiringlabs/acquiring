from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Dict, List, Optional

import django_acquiring.domain.decision_logic as dl
from django_acquiring import domain
from django_acquiring.protocols.enums import OperationStatusEnum, OperationTypeEnum
from django_acquiring.protocols.flows import payment_operation_type

if TYPE_CHECKING:
    from django_acquiring.protocols.flows import AbstractBlock, AbstractOperationResponse
    from django_acquiring.protocols.payments import AbstractPaymentMethod
    from django_acquiring.protocols.repositories import AbstractRepository


@dataclass
class OperationResponse:
    status: OperationStatusEnum
    payment_method: Optional["AbstractPaymentMethod"]
    type: OperationTypeEnum
    error_message: str | None = None
    actions: List[Dict] = field(default_factory=list)


# TODO Decorate this class to ensure that all payment_operation_types are implemented as methods
@dataclass(frozen=True)
class PaymentFlow:
    repository: "AbstractRepository"
    operations_repository: "AbstractRepository"

    initialize_block: "AbstractBlock"
    process_actions_block: "AbstractBlock"

    pay_blocks: List["AbstractBlock"]
    after_pay_blocks: List["AbstractBlock"]

    confirm_blocks: List["AbstractBlock"]
    after_confirm_blocks: List["AbstractBlock"]

    @payment_operation_type
    def initialize(self, payment_method: "AbstractPaymentMethod") -> "AbstractOperationResponse":
        # Refresh the payment from the database
        try:
            payment_method = self.repository.get(id=payment_method.id)
        except domain.PaymentMethod.DoesNotExist:
            return OperationResponse(
                status=OperationStatusEnum.failed,
                payment_method=None,
                error_message="PaymentMethod not found",
                type=OperationTypeEnum.initialize,
            )

        # Verify that the payment can go through this operation type
        if not dl.can_initialize(payment_method):
            return OperationResponse(
                status=OperationStatusEnum.failed,
                payment_method=None,
                error_message="PaymentMethod cannot go through this operation",
                type=OperationTypeEnum.initialize,
            )

        # Create Started PaymentOperation
        self.operations_repository.add(
            payment_method=payment_method,
            type=OperationTypeEnum.initialize,
            status=OperationStatusEnum.started,
        )

        # Run Operation Block
        block_response = self.initialize_block.run(payment_method=payment_method)

        # Validate that status is one of the expected ones
        if block_response.status not in [
            OperationStatusEnum.completed,
            OperationStatusEnum.failed,
            OperationStatusEnum.requires_action,
        ]:
            self.operations_repository.add(
                payment_method=payment_method,
                type=OperationTypeEnum.initialize,  # TODO Refer to function name rather than explicit input in all cases
                status=OperationStatusEnum.failed,
            )
            return OperationResponse(
                status=OperationStatusEnum.failed,
                payment_method=payment_method,
                type=OperationTypeEnum.initialize,  # TODO Refer to function name rather than explicit input in all cases
                error_message=f"Invalid status {block_response.status}",
            )
        if block_response.status == OperationStatusEnum.requires_action and not block_response.actions:
            self.operations_repository.add(
                payment_method=payment_method,
                type=OperationTypeEnum.initialize,
                status=OperationStatusEnum.failed,
            )
            return OperationResponse(
                status=OperationStatusEnum.failed,
                payment_method=payment_method,
                type=OperationTypeEnum.initialize,
                error_message="Status is require actions, but no actions were provided",
            )

        # Create PaymentOperation with the outcome
        self.operations_repository.add(
            payment_method=payment_method,
            type=OperationTypeEnum.initialize,
            status=block_response.status,
        )

        # Return Response
        if block_response.status == OperationStatusEnum.completed:
            return self.__pay(payment_method)

        return OperationResponse(
            status=block_response.status,
            actions=block_response.actions,
            payment_method=payment_method,
            type=OperationTypeEnum.initialize,
        )

    @payment_operation_type
    def process_actions(
        self, payment_method: "AbstractPaymentMethod", action_data: Dict
    ) -> "AbstractOperationResponse":
        # Refresh the payment from the database
        try:
            payment_method = self.repository.get(id=payment_method.id)
        except domain.PaymentMethod.DoesNotExist:
            return OperationResponse(
                status=OperationStatusEnum.failed,
                payment_method=None,
                error_message="PaymentMethod not found",
                type=OperationTypeEnum.process_actions,
            )

        # Verify that the payment can go through this operation type
        if not dl.can_process_actions(payment_method):
            return OperationResponse(
                status=OperationStatusEnum.failed,
                payment_method=None,
                error_message="PaymentMethod cannot go through this operation",
                type=OperationTypeEnum.process_actions,
            )

        # Create Started PaymentOperation
        self.operations_repository.add(
            payment_method=payment_method,
            type=OperationTypeEnum.process_actions,
            status=OperationStatusEnum.started,
        )

        # Run Operation Block
        block_response = self.process_actions_block.run(payment_method=payment_method, action_data=action_data)

        # Validate that status is one of the expected ones
        if block_response.status not in [
            OperationStatusEnum.completed,
            OperationStatusEnum.failed,
        ]:
            self.operations_repository.add(
                payment_method=payment_method,
                type=OperationTypeEnum.process_actions,
                status=OperationStatusEnum.failed,
            )
            return OperationResponse(
                status=OperationStatusEnum.failed,
                payment_method=payment_method,
                type=OperationTypeEnum.process_actions,
                error_message=f"Invalid status {block_response.status}",
            )

        # Create PaymentOperation with the outcome
        self.operations_repository.add(
            payment_method=payment_method,
            type=OperationTypeEnum.process_actions,
            status=block_response.status,
        )

        # Return Response
        if block_response.status == OperationStatusEnum.completed:
            return self.__pay(payment_method)

        return OperationResponse(
            status=block_response.status,
            actions=block_response.actions,
            payment_method=payment_method,
            type=OperationTypeEnum.process_actions,
        )

    @payment_operation_type
    def __pay(self, payment_method: "AbstractPaymentMethod") -> "AbstractOperationResponse":
        # No need to refresh from DB

        # Verify that the payment can go through this operation type
        if not dl.can_pay(payment_method):
            return OperationResponse(
                status=OperationStatusEnum.failed,
                payment_method=None,
                error_message="PaymentMethod cannot go through this operation",
                type=OperationTypeEnum.pay,
            )

        # Create Started PaymentOperation
        self.operations_repository.add(
            payment_method=payment_method,
            type=OperationTypeEnum.pay,
            status=OperationStatusEnum.started,
        )

        # Run Operation Blocks
        responses = [block.run(payment_method) for block in self.pay_blocks]

        has_completed = all([response.status == OperationStatusEnum.completed for response in responses])

        is_pending = any([response.status == OperationStatusEnum.pending for response in responses])

        if has_completed:
            status = OperationStatusEnum.completed
        elif not has_completed and is_pending:
            status = OperationStatusEnum.pending
        else:
            # TODO Allow for the possibility of any block forcing the response to be failed
            status = OperationStatusEnum.failed

        # Create PaymentOperation with the outcome
        self.operations_repository.add(
            payment_method=payment_method,
            type=OperationTypeEnum.pay,
            status=status,
        )

        # Return Response
        return OperationResponse(
            status=status,
            payment_method=payment_method,
            type=OperationTypeEnum.pay,
            error_message=", ".join(
                [response.error_message for response in responses if response.error_message is not None]
            ),
        )

    @payment_operation_type
    def after_pay(self, payment_method: "AbstractPaymentMethod") -> "AbstractOperationResponse":
        # Refresh the payment from the database
        try:
            payment_method = self.repository.get(id=payment_method.id)
        except domain.PaymentMethod.DoesNotExist:
            return OperationResponse(
                status=OperationStatusEnum.failed,
                payment_method=None,
                error_message="PaymentMethod not found",
                type=OperationTypeEnum.after_pay,
            )

        # Verify that the payment can go through this operation type
        if not dl.can_after_pay(payment_method):
            return OperationResponse(
                status=OperationStatusEnum.failed,
                payment_method=None,
                error_message="PaymentMethod cannot go through this operation",
                type=OperationTypeEnum.after_pay,
            )

        # Create Started PaymentOperation
        self.operations_repository.add(
            payment_method=payment_method,
            type=OperationTypeEnum.after_pay,
            status=OperationStatusEnum.started,
        )

        # Run Operation Blocks
        responses = [block.run(payment_method) for block in self.after_pay_blocks]

        has_completed = all([response.status == OperationStatusEnum.completed for response in responses])

        if not has_completed:
            self.operations_repository.add(
                payment_method=payment_method,
                type=OperationTypeEnum.after_pay,
                status=OperationStatusEnum.failed,
            )
            return OperationResponse(
                status=OperationStatusEnum.failed,
                payment_method=payment_method,
                type=OperationTypeEnum.after_pay,
            )

        status = OperationStatusEnum.completed if has_completed else OperationStatusEnum.failed

        # Create PaymentOperation with the outcome
        self.operations_repository.add(
            payment_method=payment_method,
            type=OperationTypeEnum.after_pay,
            status=status,
        )

        # Return Response
        return OperationResponse(
            status=status,
            payment_method=payment_method,
            type=OperationTypeEnum.after_pay,
        )

    @payment_operation_type
    def confirm(self, payment_method: "AbstractPaymentMethod") -> "AbstractOperationResponse":
        # Refresh the payment from the database
        try:
            payment_method = self.repository.get(id=payment_method.id)
        except domain.PaymentMethod.DoesNotExist:
            return OperationResponse(
                status=OperationStatusEnum.failed,
                payment_method=None,
                error_message="PaymentMethod not found",
                type=OperationTypeEnum.confirm,
            )

        # Verify that the payment can go through this operation type
        if not dl.can_confirm(payment_method):
            return OperationResponse(
                status=OperationStatusEnum.failed,
                payment_method=None,
                error_message="PaymentMethod cannot go through this operation",
                type=OperationTypeEnum.confirm,
            )

        # Create Started PaymentOperation
        self.operations_repository.add(
            payment_method=payment_method,
            type=OperationTypeEnum.confirm,
            status=OperationStatusEnum.started,
        )

        # Run Operation Blocks
        responses = [block.run(payment_method) for block in self.confirm_blocks]

        has_completed = all([response.status == OperationStatusEnum.completed for response in responses])

        is_pending = any([response.status == OperationStatusEnum.pending for response in responses])

        if has_completed:
            status = OperationStatusEnum.completed
        elif not has_completed and is_pending:
            status = OperationStatusEnum.pending
        else:
            # TODO Allow for the possibility of any block forcing the response to be failed
            status = OperationStatusEnum.failed

        # Create PaymentOperation with the outcome
        self.operations_repository.add(
            payment_method=payment_method,
            type=OperationTypeEnum.confirm,
            status=status,
        )

        # Return Response
        return OperationResponse(
            status=status,
            payment_method=payment_method,
            type=OperationTypeEnum.confirm,
            error_message=", ".join(
                [response.error_message for response in responses if response.error_message is not None]
            ),
        )

    @payment_operation_type
    def after_confirm(self, payment_method: "AbstractPaymentMethod") -> "AbstractOperationResponse":
        # Refresh the payment from the database
        try:
            payment_method = self.repository.get(id=payment_method.id)
        except domain.PaymentMethod.DoesNotExist:
            return OperationResponse(
                status=OperationStatusEnum.failed,
                payment_method=None,
                error_message="PaymentMethod not found",
                type=OperationTypeEnum.after_confirm,
            )

        # Verify that the payment can go through this operation type
        if not dl.can_after_confirm(payment_method):
            return OperationResponse(
                status=OperationStatusEnum.failed,
                payment_method=None,
                error_message="PaymentMethod cannot go through this operation",
                type=OperationTypeEnum.after_confirm,
            )

        # Create Started PaymentOperation
        self.operations_repository.add(
            payment_method=payment_method,
            type=OperationTypeEnum.after_confirm,
            status=OperationStatusEnum.started,
        )

        # Run Operation Blocks
        responses = [block.run(payment_method) for block in self.after_confirm_blocks]

        has_completed = all([response.status == OperationStatusEnum.completed for response in responses])

        is_pending = any([response.status == OperationStatusEnum.pending for response in responses])

        if has_completed:
            status = OperationStatusEnum.completed
        elif not has_completed and is_pending:
            status = OperationStatusEnum.pending
        else:
            # TODO Allow for the possibility of any block forcing the response to be failed
            status = OperationStatusEnum.failed

        # Create PaymentOperation with the outcome
        self.operations_repository.add(
            payment_method=payment_method,
            type=OperationTypeEnum.after_confirm,
            status=status,
        )

        # Return Response
        return OperationResponse(
            status=status,
            payment_method=payment_method,
            type=OperationTypeEnum.after_confirm,
            error_message=", ".join(
                [response.error_message for response in responses if response.error_message is not None]
            ),
        )
