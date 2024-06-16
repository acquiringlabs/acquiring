import functools
from dataclasses import dataclass, field
from typing import Callable, Optional, Sequence

import deal

import acquiring.domain.decision_logic as dl
from acquiring import domain, enums, protocols


def operation_type(  # type:ignore[misc]
    function: Callable[..., "protocols.OperationResponse"]
) -> Callable[..., "protocols.OperationResponse"]:
    """
    This decorator verifies that the name of this function belongs to one of enums.OperationTypeEnums.

    Raises a TypeError otherwise.
    """

    @functools.wraps(function)
    def wrapper(
        *args: Sequence,
        **kwargs: dict,
    ) -> "protocols.OperationResponse":
        if function.__name__.strip("_") not in enums.OperationTypeEnum:
            raise TypeError("This function cannot be a payment type")
        return function(*args, **kwargs)

    return wrapper


def implements_blocks(  # type:ignore[misc]
    function: Callable[..., "protocols.OperationResponse"]
) -> Callable[..., "protocols.OperationResponse"]:
    """
    This decorator verifies that the class implements the blocks used in the decorated function.

    When calling Klass.confirm, then Klass must implement confirm_block or confirm_blocks
    and it cannot be "falsy" (None or empty list).

    Raises a TypeError otherwise.
    """

    @functools.wraps(function)
    def wrapper(
        self: "protocols.PaymentMethodSaga",
        payment_method: "protocols.PaymentMethod",
        *args: Sequence,
        **kwargs: dict,
    ) -> "protocols.OperationResponse":

        # Some of the types have blocks, other just block. Need to check for both.
        operation_type_name = function.__name__.strip("_")
        if (
            hasattr(self, f"{operation_type_name}_block")
            and getattr(self, f"{operation_type_name}_block")
            or hasattr(self, f"{operation_type_name}_blocks")
            and getattr(self, f"{operation_type_name}_blocks")
        ):
            return function(self, payment_method, *args, **kwargs)

        raise TypeError("This PaymentMethodSaga does not implement blocks for this operation type")

    return wrapper


def refresh_payment_method(  # type:ignore[misc]
    function: Callable[..., "protocols.OperationResponse"]
) -> Callable[..., "protocols.OperationResponse"]:
    """
    Refresh the payment from the database, or force an early failed OperationResponse otherwise.
    """

    @functools.wraps(function)
    def wrapper(
        self: "protocols.PaymentMethodSaga",
        payment_method: "protocols.PaymentMethod",
        *args: Sequence,
        **kwargs: dict,
    ) -> "protocols.OperationResponse":
        try:
            with self.unit_of_work as uow:
                payment_method = uow.payment_methods.get(id=payment_method.id)
        except domain.PaymentMethod.DoesNotExist:
            return OperationResponse(
                status=enums.OperationStatusEnum.FAILED,
                payment_method=None,
                error_message="PaymentMethod not found",
                type=enums.OperationTypeEnum(function.__name__),  # already valid thanks to @operation_type
            )
        return function(self, payment_method, *args, **kwargs)

    return wrapper


@dataclass
class OperationResponse:
    """Represents the outcome of a PaymentMethodSaga operation type method execution"""

    status: enums.OperationStatusEnum
    payment_method: Optional["protocols.PaymentMethod"]
    type: enums.OperationTypeEnum
    error_message: Optional[str] = None
    actions: list[dict] = field(default_factory=list)


# TODO Decorate this class to ensure that all operation_types are implemented as methods
@dataclass
class PaymentMethodSaga:
    """
    Context class that defines what's common across all Payment Methods and their execution.

    What's specific to each payment method is implemented inside each one of the block(s).
    """

    unit_of_work: "protocols.UnitOfWork"

    initialize_block: Optional["protocols.Block"]  # If not provided, it will create a PO with status NOT_PERFORMED
    process_action_block: Optional["protocols.Block"]  # Only required when payment method requires customer actions

    pay_block: "protocols.Block"
    after_pay_blocks: list["protocols.Block"]  # Only required when payment method is paid asynchronously

    confirm_block: Optional["protocols.Block"]  # Only required for dual message payments
    after_confirm_blocks: list["protocols.Block"]  # Only required when payment method is confirmed asynchronously

    @deal.safe  # TODO Implement deal.has to consider database access
    @operation_type
    @refresh_payment_method
    def initialize(self, payment_method: "protocols.PaymentMethod") -> "protocols.OperationResponse":
        # Verify that the payment can go through this operation type
        if not dl.can_initialize(payment_method):
            return OperationResponse(
                status=enums.OperationStatusEnum.FAILED,
                payment_method=None,
                error_message="PaymentMethod cannot go through this operation",
                type=enums.OperationTypeEnum.INITIALIZE,
            )

        # Create Started OperationEvent
        with self.unit_of_work as uow:
            uow.operation_events.add(
                payment_method=payment_method,
                type=enums.OperationTypeEnum.INITIALIZE,
                status=enums.OperationStatusEnum.STARTED,
            )
            uow.commit()

        # Run Operation Block if it exists
        if self.initialize_block is None:
            with self.unit_of_work as uow:
                uow.operation_events.add(
                    payment_method=payment_method,
                    type=enums.OperationTypeEnum.INITIALIZE,
                    status=enums.OperationStatusEnum.NOT_PERFORMED,
                )
                uow.commit()
            return self.__pay(payment_method)

        block_response = self.initialize_block.run(unit_of_work=self.unit_of_work, payment_method=payment_method)

        # Validate that status is one of the expected ones
        if block_response.status not in [
            enums.OperationStatusEnum.COMPLETED,
            enums.OperationStatusEnum.FAILED,
            enums.OperationStatusEnum.REQUIRES_ACTION,
        ]:
            with self.unit_of_work as uow:
                uow.operation_events.add(
                    payment_method=payment_method,
                    type=enums.OperationTypeEnum.INITIALIZE,  # TODO Refer to function name rather than explicit input in all cases
                    status=enums.OperationStatusEnum.FAILED,
                )
                uow.commit()
            return OperationResponse(
                status=enums.OperationStatusEnum.FAILED,
                payment_method=payment_method,
                type=enums.OperationTypeEnum.INITIALIZE,  # TODO Refer to function name rather than explicit input in all cases
                error_message=f"Invalid status {block_response.status}",
            )
        if block_response.status == enums.OperationStatusEnum.REQUIRES_ACTION and not block_response.actions:
            with self.unit_of_work as uow:
                uow.operation_events.add(
                    payment_method=payment_method,
                    type=enums.OperationTypeEnum.INITIALIZE,
                    status=enums.OperationStatusEnum.FAILED,
                )
                uow.commit()
            return OperationResponse(
                status=enums.OperationStatusEnum.FAILED,
                payment_method=payment_method,
                type=enums.OperationTypeEnum.INITIALIZE,
                error_message="Status is require actions, but no actions were provided",
            )

        # Create OperationEvent with the outcome
        with self.unit_of_work as uow:
            uow.operation_events.add(
                payment_method=payment_method,
                type=enums.OperationTypeEnum.INITIALIZE,
                status=block_response.status,
            )
            uow.commit()

        # Return Response
        if block_response.status == enums.OperationStatusEnum.COMPLETED:
            return self.__pay(payment_method)

        return OperationResponse(
            status=block_response.status,
            actions=block_response.actions,
            payment_method=payment_method,
            type=enums.OperationTypeEnum.INITIALIZE,
        )

    @deal.reason(TypeError, lambda self, payment_method, action_data: not self.process_action_block)
    @operation_type
    @implements_blocks
    @refresh_payment_method
    def process_action(
        self, payment_method: "protocols.PaymentMethod", action_data: dict
    ) -> "protocols.OperationResponse":
        # Verify that the payment can go through this operation type

        if not dl.can_process_action(payment_method):
            return OperationResponse(
                status=enums.OperationStatusEnum.FAILED,
                payment_method=None,
                error_message="PaymentMethod cannot go through this operation",
                type=enums.OperationTypeEnum.PROCESS_ACTION,
            )

        # Create Started OperationEvent
        with self.unit_of_work as uow:
            uow.operation_events.add(
                payment_method=payment_method,
                type=enums.OperationTypeEnum.PROCESS_ACTION,
                status=enums.OperationStatusEnum.STARTED,
            )
            uow.commit()

        if self.process_action_block is None:
            with self.unit_of_work as uow:
                uow.operation_events.add(
                    payment_method=payment_method,
                    type=enums.OperationTypeEnum.PROCESS_ACTION,
                    status=enums.OperationStatusEnum.NOT_PERFORMED,
                )
                uow.commit()
            return OperationResponse(
                status=enums.OperationStatusEnum.NOT_PERFORMED,
                payment_method=payment_method,
                type=enums.OperationTypeEnum.PROCESS_ACTION,
                error_message="PaymentMethodSaga does not include a block for this operation type",
            )

        # Run Operation Block
        block_response = self.process_action_block.run(
            unit_of_work=self.unit_of_work, payment_method=payment_method, action_data=action_data
        )

        # Validate that status is one of the expected ones
        if block_response.status not in [
            enums.OperationStatusEnum.COMPLETED,
            enums.OperationStatusEnum.FAILED,
        ]:
            with self.unit_of_work as uow:
                uow.operation_events.add(
                    payment_method=payment_method,
                    type=enums.OperationTypeEnum.PROCESS_ACTION,
                    status=enums.OperationStatusEnum.FAILED,
                )
                uow.commit()
            return OperationResponse(
                status=enums.OperationStatusEnum.FAILED,
                payment_method=payment_method,
                type=enums.OperationTypeEnum.PROCESS_ACTION,
                error_message=f"Invalid status {block_response.status}",
            )

        # Create OperationEvent with the outcome
        with self.unit_of_work as uow:
            uow.operation_events.add(
                payment_method=payment_method,
                type=enums.OperationTypeEnum.PROCESS_ACTION,
                status=block_response.status,
            )
            uow.commit()

        # Return Response
        if block_response.status == enums.OperationStatusEnum.COMPLETED:
            return self.__pay(payment_method)

        return OperationResponse(
            status=block_response.status,
            actions=block_response.actions,
            payment_method=payment_method,
            type=enums.OperationTypeEnum.PROCESS_ACTION,
        )

    @deal.pure
    @operation_type
    def __pay(self, payment_method: "protocols.PaymentMethod") -> "protocols.OperationResponse":
        # No need to refresh from DB

        # No need to verify if payment can go through a private method

        # Create Started OperationEvent
        with self.unit_of_work as uow:
            uow.operation_events.add(
                payment_method=payment_method,
                type=enums.OperationTypeEnum.PAY,
                status=enums.OperationStatusEnum.STARTED,
            )
            uow.commit()

        # Run Operation Block
        block_response = self.pay_block.run(unit_of_work=self.unit_of_work, payment_method=payment_method)

        # Create OperationEvent with the outcome
        with self.unit_of_work as uow:
            uow.operation_events.add(
                payment_method=payment_method,
                type=enums.OperationTypeEnum.PAY,
                status=block_response.status,
            )
            uow.commit()

        # Return Response
        return OperationResponse(
            status=block_response.status,
            payment_method=payment_method,
            type=enums.OperationTypeEnum.PAY,
            error_message=block_response.error_message,
        )

    @deal.reason(TypeError, lambda self, payment_method: not self.after_pay_blocks)
    @operation_type
    @implements_blocks
    @refresh_payment_method
    def after_pay(self, payment_method: "protocols.PaymentMethod") -> "protocols.OperationResponse":
        # Verify that the payment can go through this operation type
        if not dl.can_after_pay(payment_method):
            return OperationResponse(
                status=enums.OperationStatusEnum.FAILED,
                payment_method=None,
                error_message="PaymentMethod cannot go through this operation",
                type=enums.OperationTypeEnum.AFTER_PAY,
            )

        # Create Started OperationEvent
        with self.unit_of_work as uow:
            uow.operation_events.add(
                payment_method=payment_method,
                type=enums.OperationTypeEnum.AFTER_PAY,
                status=enums.OperationStatusEnum.STARTED,
            )
            uow.commit()

        # Run Operation Blocks
        responses = [
            block.run(unit_of_work=self.unit_of_work, payment_method=payment_method) for block in self.after_pay_blocks
        ]

        has_completed = all([response.status == enums.OperationStatusEnum.COMPLETED for response in responses])

        if not has_completed:
            with self.unit_of_work as uow:
                uow.operation_events.add(
                    payment_method=payment_method,
                    type=enums.OperationTypeEnum.AFTER_PAY,
                    status=enums.OperationStatusEnum.FAILED,
                )
                uow.commit()
            return OperationResponse(
                status=enums.OperationStatusEnum.FAILED,
                payment_method=payment_method,
                type=enums.OperationTypeEnum.AFTER_PAY,
            )

        status = enums.OperationStatusEnum.COMPLETED if has_completed else enums.OperationStatusEnum.FAILED

        # Create OperationEvent with the outcome
        with self.unit_of_work as uow:
            uow.operation_events.add(
                payment_method=payment_method,
                type=enums.OperationTypeEnum.AFTER_PAY,
                status=status,
            )
            uow.commit()

        # Return Response
        return OperationResponse(
            status=status,
            payment_method=payment_method,
            type=enums.OperationTypeEnum.AFTER_PAY,
        )

    @deal.reason(TypeError, lambda self, payment_method, action_data: not self.confirm_block)
    @operation_type
    @implements_blocks
    @refresh_payment_method
    def confirm(self, payment_method: "protocols.PaymentMethod") -> "protocols.OperationResponse":
        # Verify that the payment can go through this operation type
        if not dl.can_confirm(payment_method):
            return OperationResponse(
                status=enums.OperationStatusEnum.FAILED,
                payment_method=None,
                error_message="PaymentMethod cannot go through this operation",
                type=enums.OperationTypeEnum.CONFIRM,
            )

        # Create Started OperationEvent
        with self.unit_of_work as uow:
            uow.operation_events.add(
                payment_method=payment_method,
                type=enums.OperationTypeEnum.CONFIRM,
                status=enums.OperationStatusEnum.STARTED,
            )
            uow.commit()

        # Run Operation Blocks
        if self.confirm_block is None:
            with self.unit_of_work as uow:
                uow.operation_events.add(
                    payment_method=payment_method,
                    type=enums.OperationTypeEnum.CONFIRM,
                    status=enums.OperationStatusEnum.NOT_PERFORMED,
                )
                uow.commit()
            return OperationResponse(
                status=enums.OperationStatusEnum.NOT_PERFORMED,
                payment_method=payment_method,
                type=enums.OperationTypeEnum.CONFIRM,
                error_message="PaymentMethodSaga does not include a block for this operation type",
            )

        # Run Operation Block
        block_response = self.confirm_block.run(unit_of_work=self.unit_of_work, payment_method=payment_method)

        # Validate that status is one of the expected ones
        if block_response.status not in [
            enums.OperationStatusEnum.COMPLETED,
            enums.OperationStatusEnum.FAILED,
            enums.OperationStatusEnum.PENDING,
        ]:
            with self.unit_of_work as uow:
                uow.operation_events.add(
                    payment_method=payment_method,
                    type=enums.OperationTypeEnum.CONFIRM,
                    status=enums.OperationStatusEnum.FAILED,
                )
                uow.commit()
            return OperationResponse(
                status=enums.OperationStatusEnum.FAILED,
                payment_method=payment_method,
                type=enums.OperationTypeEnum.CONFIRM,
                error_message=f"Invalid status {block_response.status}",
            )

        # Create OperationEvent with the outcome
        with self.unit_of_work as uow:
            uow.operation_events.add(
                payment_method=payment_method,
                type=enums.OperationTypeEnum.CONFIRM,
                status=block_response.status,
            )
            uow.commit()

        # Return Response
        return OperationResponse(
            status=block_response.status,
            payment_method=payment_method,
            type=enums.OperationTypeEnum.CONFIRM,
            error_message=block_response.error_message,
        )

    @deal.reason(TypeError, lambda self, payment_method, action_data: not self.after_confirm_blocks)
    @operation_type
    @implements_blocks
    @refresh_payment_method
    def after_confirm(self, payment_method: "protocols.PaymentMethod") -> "protocols.OperationResponse":
        # Verify that the payment can go through this operation type
        if not dl.can_after_confirm(payment_method):
            return OperationResponse(
                status=enums.OperationStatusEnum.FAILED,
                payment_method=None,
                error_message="PaymentMethod cannot go through this operation",
                type=enums.OperationTypeEnum.AFTER_CONFIRM,
            )

        # Create Started OperationEvent
        with self.unit_of_work as uow:
            uow.operation_events.add(
                payment_method=payment_method,
                type=enums.OperationTypeEnum.AFTER_CONFIRM,
                status=enums.OperationStatusEnum.STARTED,
            )
            uow.commit()

        # Run Operation Blocks
        responses = [
            block.run(unit_of_work=self.unit_of_work, payment_method=payment_method)
            for block in self.after_confirm_blocks
        ]

        has_completed = all([response.status == enums.OperationStatusEnum.COMPLETED for response in responses])

        is_pending = any([response.status == enums.OperationStatusEnum.PENDING for response in responses])

        if has_completed:
            status = enums.OperationStatusEnum.COMPLETED
        elif not has_completed and is_pending:
            status = enums.OperationStatusEnum.PENDING
        else:
            # TODO Allow for the possibility of any block forcing the response to be failed
            status = enums.OperationStatusEnum.FAILED

        # Create OperationEvent with the outcome
        with self.unit_of_work as uow:
            uow.operation_events.add(
                payment_method=payment_method,
                type=enums.OperationTypeEnum.AFTER_CONFIRM,
                status=status,
            )
            uow.commit()

        # Return Response
        return OperationResponse(
            status=status,
            payment_method=payment_method,
            type=enums.OperationTypeEnum.AFTER_CONFIRM,
            error_message=", ".join(
                [response.error_message for response in responses if response.error_message is not None]
            ),
        )
