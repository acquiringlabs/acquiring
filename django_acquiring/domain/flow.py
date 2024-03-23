from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Optional

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
    error_message: Optional[str] = None
    actions: list[dict] = field(default_factory=list)


# TODO Decorate this class to ensure that all payment_operation_types are implemented as methods
@dataclass(frozen=True)
class PaymentFlow:
    repository: "AbstractRepository"
    operations_repository: "AbstractRepository"

    initialize_block: "AbstractBlock"
    process_action_block: "AbstractBlock"

    pay_blocks: list["AbstractBlock"]
    after_pay_blocks: list["AbstractBlock"]

    confirm_blocks: list["AbstractBlock"]
    after_confirm_blocks: list["AbstractBlock"]

    @payment_operation_type
    def initialize(self, payment_method: "AbstractPaymentMethod") -> "AbstractOperationResponse":
        # Refresh the payment from the database
        try:
            payment_method = self.repository.get(id=payment_method.id)
        except domain.PaymentMethod.DoesNotExist:
            return OperationResponse(
                status=OperationStatusEnum.FAILED,
                payment_method=None,
                error_message="PaymentMethod not found",
                type=OperationTypeEnum.INITIALIZE,
            )

        # Verify that the payment can go through this operation type
        if not dl.can_initialize(payment_method):
            return OperationResponse(
                status=OperationStatusEnum.FAILED,
                payment_method=None,
                error_message="PaymentMethod cannot go through this operation",
                type=OperationTypeEnum.INITIALIZE,
            )

        # Create Started PaymentOperation
        self.operations_repository.add(
            payment_method=payment_method,
            type=OperationTypeEnum.INITIALIZE,
            status=OperationStatusEnum.STARTED,
        )

        # Run Operation Block
        block_response = self.initialize_block.run(payment_method=payment_method)

        # Validate that status is one of the expected ones
        if block_response.status not in [
            OperationStatusEnum.COMPLETED,
            OperationStatusEnum.FAILED,
            OperationStatusEnum.REQUIRES_ACTION,
        ]:
            self.operations_repository.add(
                payment_method=payment_method,
                type=OperationTypeEnum.INITIALIZE,  # TODO Refer to function name rather than explicit input in all cases
                status=OperationStatusEnum.FAILED,
            )
            return OperationResponse(
                status=OperationStatusEnum.FAILED,
                payment_method=payment_method,
                type=OperationTypeEnum.INITIALIZE,  # TODO Refer to function name rather than explicit input in all cases
                error_message=f"Invalid status {block_response.status}",
            )
        if block_response.status == OperationStatusEnum.REQUIRES_ACTION and not block_response.actions:
            self.operations_repository.add(
                payment_method=payment_method,
                type=OperationTypeEnum.INITIALIZE,
                status=OperationStatusEnum.FAILED,
            )
            return OperationResponse(
                status=OperationStatusEnum.FAILED,
                payment_method=payment_method,
                type=OperationTypeEnum.INITIALIZE,
                error_message="Status is require actions, but no actions were provided",
            )

        # Create PaymentOperation with the outcome
        self.operations_repository.add(
            payment_method=payment_method,
            type=OperationTypeEnum.INITIALIZE,
            status=block_response.status,
        )

        # Return Response
        if block_response.status == OperationStatusEnum.COMPLETED:
            return self.__pay(payment_method)

        return OperationResponse(
            status=block_response.status,
            actions=block_response.actions,
            payment_method=payment_method,
            type=OperationTypeEnum.INITIALIZE,
        )

    @payment_operation_type
    def process_action(self, payment_method: "AbstractPaymentMethod", action_data: dict) -> "AbstractOperationResponse":
        # Refresh the payment from the database
        try:
            payment_method = self.repository.get(id=payment_method.id)
        except domain.PaymentMethod.DoesNotExist:
            return OperationResponse(
                status=OperationStatusEnum.FAILED,
                payment_method=None,
                error_message="PaymentMethod not found",
                type=OperationTypeEnum.PROCESS_ACTION,
            )

        # Verify that the payment can go through this operation type
        if not dl.can_process_action(payment_method):
            return OperationResponse(
                status=OperationStatusEnum.FAILED,
                payment_method=None,
                error_message="PaymentMethod cannot go through this operation",
                type=OperationTypeEnum.PROCESS_ACTION,
            )

        # Create Started PaymentOperation
        self.operations_repository.add(
            payment_method=payment_method,
            type=OperationTypeEnum.PROCESS_ACTION,
            status=OperationStatusEnum.STARTED,
        )

        # Run Operation Block
        block_response = self.process_action_block.run(payment_method=payment_method, action_data=action_data)

        # Validate that status is one of the expected ones
        if block_response.status not in [
            OperationStatusEnum.COMPLETED,
            OperationStatusEnum.FAILED,
        ]:
            self.operations_repository.add(
                payment_method=payment_method,
                type=OperationTypeEnum.PROCESS_ACTION,
                status=OperationStatusEnum.FAILED,
            )
            return OperationResponse(
                status=OperationStatusEnum.FAILED,
                payment_method=payment_method,
                type=OperationTypeEnum.PROCESS_ACTION,
                error_message=f"Invalid status {block_response.status}",
            )

        # Create PaymentOperation with the outcome
        self.operations_repository.add(
            payment_method=payment_method,
            type=OperationTypeEnum.PROCESS_ACTION,
            status=block_response.status,
        )

        # Return Response
        if block_response.status == OperationStatusEnum.COMPLETED:
            return self.__pay(payment_method)

        return OperationResponse(
            status=block_response.status,
            actions=block_response.actions,
            payment_method=payment_method,
            type=OperationTypeEnum.PROCESS_ACTION,
        )

    @payment_operation_type
    def __pay(self, payment_method: "AbstractPaymentMethod") -> "AbstractOperationResponse":
        # No need to refresh from DB

        # Verify that the payment can go through this operation type
        if not dl.can_pay(payment_method):
            return OperationResponse(
                status=OperationStatusEnum.FAILED,
                payment_method=None,
                error_message="PaymentMethod cannot go through this operation",
                type=OperationTypeEnum.PAY,
            )

        # Create Started PaymentOperation
        self.operations_repository.add(
            payment_method=payment_method,
            type=OperationTypeEnum.PAY,
            status=OperationStatusEnum.STARTED,
        )

        # Run Operation Blocks
        responses = [block.run(payment_method) for block in self.pay_blocks]

        has_completed = all([response.status == OperationStatusEnum.COMPLETED for response in responses])

        is_pending = any([response.status == OperationStatusEnum.PENDING for response in responses])

        if has_completed:
            status = OperationStatusEnum.COMPLETED
        elif not has_completed and is_pending:
            status = OperationStatusEnum.PENDING
        else:
            # TODO Allow for the possibility of any block forcing the response to be failed
            status = OperationStatusEnum.FAILED

        # Create PaymentOperation with the outcome
        self.operations_repository.add(
            payment_method=payment_method,
            type=OperationTypeEnum.PAY,
            status=status,
        )

        # Return Response
        return OperationResponse(
            status=status,
            payment_method=payment_method,
            type=OperationTypeEnum.PAY,
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
                status=OperationStatusEnum.FAILED,
                payment_method=None,
                error_message="PaymentMethod not found",
                type=OperationTypeEnum.AFTER_PAY,
            )

        # Verify that the payment can go through this operation type
        if not dl.can_after_pay(payment_method):
            return OperationResponse(
                status=OperationStatusEnum.FAILED,
                payment_method=None,
                error_message="PaymentMethod cannot go through this operation",
                type=OperationTypeEnum.AFTER_PAY,
            )

        # Create Started PaymentOperation
        self.operations_repository.add(
            payment_method=payment_method,
            type=OperationTypeEnum.AFTER_PAY,
            status=OperationStatusEnum.STARTED,
        )

        # Run Operation Blocks
        responses = [block.run(payment_method) for block in self.after_pay_blocks]

        has_completed = all([response.status == OperationStatusEnum.COMPLETED for response in responses])

        if not has_completed:
            self.operations_repository.add(
                payment_method=payment_method,
                type=OperationTypeEnum.AFTER_PAY,
                status=OperationStatusEnum.FAILED,
            )
            return OperationResponse(
                status=OperationStatusEnum.FAILED,
                payment_method=payment_method,
                type=OperationTypeEnum.AFTER_PAY,
            )

        status = OperationStatusEnum.COMPLETED if has_completed else OperationStatusEnum.FAILED

        # Create PaymentOperation with the outcome
        self.operations_repository.add(
            payment_method=payment_method,
            type=OperationTypeEnum.AFTER_PAY,
            status=status,
        )

        # Return Response
        return OperationResponse(
            status=status,
            payment_method=payment_method,
            type=OperationTypeEnum.AFTER_PAY,
        )

    @payment_operation_type
    def confirm(self, payment_method: "AbstractPaymentMethod") -> "AbstractOperationResponse":
        # Refresh the payment from the database
        try:
            payment_method = self.repository.get(id=payment_method.id)
        except domain.PaymentMethod.DoesNotExist:
            return OperationResponse(
                status=OperationStatusEnum.FAILED,
                payment_method=None,
                error_message="PaymentMethod not found",
                type=OperationTypeEnum.CONFIRM,
            )

        # Verify that the payment can go through this operation type
        if not dl.can_confirm(payment_method):
            return OperationResponse(
                status=OperationStatusEnum.FAILED,
                payment_method=None,
                error_message="PaymentMethod cannot go through this operation",
                type=OperationTypeEnum.CONFIRM,
            )

        # Create Started PaymentOperation
        self.operations_repository.add(
            payment_method=payment_method,
            type=OperationTypeEnum.CONFIRM,
            status=OperationStatusEnum.STARTED,
        )

        # Run Operation Blocks
        responses = [block.run(payment_method) for block in self.confirm_blocks]

        has_completed = all([response.status == OperationStatusEnum.COMPLETED for response in responses])

        is_pending = any([response.status == OperationStatusEnum.PENDING for response in responses])

        if has_completed:
            status = OperationStatusEnum.COMPLETED
        elif not has_completed and is_pending:
            status = OperationStatusEnum.PENDING
        else:
            # TODO Allow for the possibility of any block forcing the response to be failed
            status = OperationStatusEnum.FAILED

        # Create PaymentOperation with the outcome
        self.operations_repository.add(
            payment_method=payment_method,
            type=OperationTypeEnum.CONFIRM,
            status=status,
        )

        # Return Response
        return OperationResponse(
            status=status,
            payment_method=payment_method,
            type=OperationTypeEnum.CONFIRM,
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
                status=OperationStatusEnum.FAILED,
                payment_method=None,
                error_message="PaymentMethod not found",
                type=OperationTypeEnum.AFTER_CONFIRM,
            )

        # Verify that the payment can go through this operation type
        if not dl.can_after_confirm(payment_method):
            return OperationResponse(
                status=OperationStatusEnum.FAILED,
                payment_method=None,
                error_message="PaymentMethod cannot go through this operation",
                type=OperationTypeEnum.AFTER_CONFIRM,
            )

        # Create Started PaymentOperation
        self.operations_repository.add(
            payment_method=payment_method,
            type=OperationTypeEnum.AFTER_CONFIRM,
            status=OperationStatusEnum.STARTED,
        )

        # Run Operation Blocks
        responses = [block.run(payment_method) for block in self.after_confirm_blocks]

        has_completed = all([response.status == OperationStatusEnum.COMPLETED for response in responses])

        is_pending = any([response.status == OperationStatusEnum.PENDING for response in responses])

        if has_completed:
            status = OperationStatusEnum.COMPLETED
        elif not has_completed and is_pending:
            status = OperationStatusEnum.PENDING
        else:
            # TODO Allow for the possibility of any block forcing the response to be failed
            status = OperationStatusEnum.FAILED

        # Create PaymentOperation with the outcome
        self.operations_repository.add(
            payment_method=payment_method,
            type=OperationTypeEnum.AFTER_CONFIRM,
            status=status,
        )

        # Return Response
        return OperationResponse(
            status=status,
            payment_method=payment_method,
            type=OperationTypeEnum.AFTER_CONFIRM,
            error_message=", ".join(
                [response.error_message for response in responses if response.error_message is not None]
            ),
        )
