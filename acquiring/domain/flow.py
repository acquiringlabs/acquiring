import functools
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Callable, Optional, Sequence

import acquiring.domain.decision_logic as dl
from acquiring import domain
from acquiring.enums import OperationStatusEnum, OperationTypeEnum

if TYPE_CHECKING:
    from acquiring import protocols


def payment_operation_type(  # type:ignore[misc]
    function: Callable[..., "protocols.AbstractOperationResponse"]
) -> Callable[..., "protocols.AbstractOperationResponse"]:
    """
    This decorator verifies that the name of this function belongs to one of the OperationTypeEnums

    >>> def initialize(): pass
    >>> payment_operation_type(initialize)()
    >>> def bad_name(): pass
    >>> payment_operation_type(bad_name)()
    Traceback (most recent call last):
        ...
    TypeError: This function cannot be a payment type

    Also, private methods that start with double underscore are allowed.
    This is helpful to make pay a private method.

    >>> def __bad_name(): pass
    >>> payment_operation_type(__bad_name)()
    Traceback (most recent call last):
        ...
    TypeError: This function cannot be a payment type
    >>> def __pay(): pass
    >>> payment_operation_type(__pay)()
    """

    @functools.wraps(function)
    def wrapper(
        *args: Sequence,
        **kwargs: dict,
    ) -> "protocols.AbstractOperationResponse":
        if function.__name__ not in OperationTypeEnum:

            # Private methods that start with double _ and have a name that belongs to enum are also allowed
            if function.__name__.startswith("__") and function.__name__[2:] in OperationTypeEnum:
                return function(*args, **kwargs)

            raise TypeError("This function cannot be a payment type")

        return function(*args, **kwargs)

    return wrapper


def refresh_payment_method(  # type:ignore[misc]
    function: Callable[..., "protocols.AbstractOperationResponse"]
) -> Callable[..., "protocols.AbstractOperationResponse"]:
    """
    Refresh the payment from the database, or force an early failed OperationResponse otherwise.
    """

    @functools.wraps(function)
    def wrapper(
        self: "protocols.AbstractPaymentFlow",
        payment_method: "protocols.AbstractPaymentMethod",
        *args: Sequence,
        **kwargs: dict,
    ) -> "protocols.AbstractOperationResponse":
        try:
            payment_method = self.payment_method_repository.get(id=payment_method.id)
        except domain.PaymentMethod.DoesNotExist:
            return OperationResponse(
                status=OperationStatusEnum.FAILED,
                payment_method=None,
                error_message="PaymentMethod not found",
                type=OperationTypeEnum(function.__name__),  # already valid thanks to @payment_operation_type
            )
        return function(self, payment_method, *args, **kwargs)

    return wrapper


@dataclass
class OperationResponse:
    status: OperationStatusEnum
    payment_method: Optional["protocols.AbstractPaymentMethod"]
    type: OperationTypeEnum
    error_message: Optional[str] = None
    actions: list[dict] = field(default_factory=list)


# TODO Decorate this class to ensure that all payment_operation_types are implemented as methods
@dataclass
class PaymentFlow:
    payment_method_repository: "protocols.AbstractRepository"
    payment_operation_repository: "protocols.AbstractRepository"

    initialize_block: Optional["protocols.AbstractBlock"]
    process_action_block: Optional["protocols.AbstractBlock"]

    pay_blocks: list["protocols.AbstractBlock"]
    after_pay_blocks: list["protocols.AbstractBlock"]

    confirm_block: Optional["protocols.AbstractBlock"]
    after_confirm_blocks: list["protocols.AbstractBlock"]

    @payment_operation_type
    @refresh_payment_method
    def initialize(self, payment_method: "protocols.AbstractPaymentMethod") -> "protocols.AbstractOperationResponse":
        # Verify that the payment can go through this operation type
        if not dl.can_initialize(payment_method):
            return OperationResponse(
                status=OperationStatusEnum.FAILED,
                payment_method=None,
                error_message="PaymentMethod cannot go through this operation",
                type=OperationTypeEnum.INITIALIZE,
            )

        # Create Started PaymentOperation
        self.payment_operation_repository.add(
            payment_method=payment_method,
            type=OperationTypeEnum.INITIALIZE,
            status=OperationStatusEnum.STARTED,
        )

        # Run Operation Block if it exists
        if self.initialize_block is None:
            self.payment_operation_repository.add(
                payment_method=payment_method,
                type=OperationTypeEnum.INITIALIZE,
                status=OperationStatusEnum.NOT_PERFORMED,
            )
            return self.__pay(payment_method)

        block_response = self.initialize_block.run(payment_method=payment_method)

        # Validate that status is one of the expected ones
        if block_response.status not in [
            OperationStatusEnum.COMPLETED,
            OperationStatusEnum.FAILED,
            OperationStatusEnum.REQUIRES_ACTION,
        ]:
            self.payment_operation_repository.add(
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
            self.payment_operation_repository.add(
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
        self.payment_operation_repository.add(
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
    @refresh_payment_method
    def process_action(
        self, payment_method: "protocols.AbstractPaymentMethod", action_data: dict
    ) -> "protocols.AbstractOperationResponse":
        # Verify that the payment can go through this operation type

        if not dl.can_process_action(payment_method):
            return OperationResponse(
                status=OperationStatusEnum.FAILED,
                payment_method=None,
                error_message="PaymentMethod cannot go through this operation",
                type=OperationTypeEnum.PROCESS_ACTION,
            )

        # Create Started PaymentOperation
        self.payment_operation_repository.add(
            payment_method=payment_method,
            type=OperationTypeEnum.PROCESS_ACTION,
            status=OperationStatusEnum.STARTED,
        )

        if self.process_action_block is None:
            self.payment_operation_repository.add(
                payment_method=payment_method,
                type=OperationTypeEnum.PROCESS_ACTION,
                status=OperationStatusEnum.NOT_PERFORMED,
            )
            return OperationResponse(
                status=OperationStatusEnum.NOT_PERFORMED,
                payment_method=payment_method,
                type=OperationTypeEnum.PROCESS_ACTION,
                error_message="PaymentFlow does not include a block for this operation type",
            )

        # Run Operation Block
        block_response = self.process_action_block.run(payment_method=payment_method, action_data=action_data)

        # Validate that status is one of the expected ones
        if block_response.status not in [
            OperationStatusEnum.COMPLETED,
            OperationStatusEnum.FAILED,
        ]:
            self.payment_operation_repository.add(
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
        self.payment_operation_repository.add(
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
    def __pay(self, payment_method: "protocols.AbstractPaymentMethod") -> "protocols.AbstractOperationResponse":
        # No need to refresh from DB

        # No need to verify if payment can go through a private method

        # Create Started PaymentOperation
        self.payment_operation_repository.add(
            payment_method=payment_method,
            type=OperationTypeEnum.PAY,
            status=OperationStatusEnum.STARTED,
        )

        # Run Operation Blocks
        responses = []
        actions = []
        for block in self.pay_blocks:
            response = block.run(payment_method)
            responses.append(response)
            actions += response.actions

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
        self.payment_operation_repository.add(
            payment_method=payment_method,
            type=OperationTypeEnum.PAY,
            status=status,
        )

        # Return Response
        return OperationResponse(
            status=status,
            payment_method=payment_method,
            actions=actions,
            type=OperationTypeEnum.PAY,
            error_message=", ".join(
                [response.error_message for response in responses if response.error_message is not None]
            ),
        )

    @payment_operation_type
    @refresh_payment_method
    def after_pay(self, payment_method: "protocols.AbstractPaymentMethod") -> "protocols.AbstractOperationResponse":
        # Verify that the payment can go through this operation type
        if not dl.can_after_pay(payment_method):
            return OperationResponse(
                status=OperationStatusEnum.FAILED,
                payment_method=None,
                error_message="PaymentMethod cannot go through this operation",
                type=OperationTypeEnum.AFTER_PAY,
            )

        # Create Started PaymentOperation
        self.payment_operation_repository.add(
            payment_method=payment_method,
            type=OperationTypeEnum.AFTER_PAY,
            status=OperationStatusEnum.STARTED,
        )

        # Run Operation Blocks
        responses = [block.run(payment_method) for block in self.after_pay_blocks]

        has_completed = all([response.status == OperationStatusEnum.COMPLETED for response in responses])

        if not has_completed:
            self.payment_operation_repository.add(
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
        self.payment_operation_repository.add(
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
    @refresh_payment_method
    def confirm(self, payment_method: "protocols.AbstractPaymentMethod") -> "protocols.AbstractOperationResponse":
        # Verify that the payment can go through this operation type
        if not dl.can_confirm(payment_method):
            return OperationResponse(
                status=OperationStatusEnum.FAILED,
                payment_method=None,
                error_message="PaymentMethod cannot go through this operation",
                type=OperationTypeEnum.CONFIRM,
            )

        # Create Started PaymentOperation
        self.payment_operation_repository.add(
            payment_method=payment_method,
            type=OperationTypeEnum.CONFIRM,
            status=OperationStatusEnum.STARTED,
        )

        # Run Operation Blocks
        if self.confirm_block is None:
            self.payment_operation_repository.add(
                payment_method=payment_method,
                type=OperationTypeEnum.CONFIRM,
                status=OperationStatusEnum.NOT_PERFORMED,
            )
            return OperationResponse(
                status=OperationStatusEnum.NOT_PERFORMED,
                payment_method=payment_method,
                type=OperationTypeEnum.CONFIRM,
                error_message="PaymentFlow does not include a block for this operation type",
            )

        # Run Operation Block
        block_response = self.confirm_block.run(payment_method=payment_method)

        # Validate that status is one of the expected ones
        if block_response.status not in [
            OperationStatusEnum.COMPLETED,
            OperationStatusEnum.FAILED,
            OperationStatusEnum.PENDING,
        ]:
            self.payment_operation_repository.add(
                payment_method=payment_method,
                type=OperationTypeEnum.CONFIRM,
                status=OperationStatusEnum.FAILED,
            )
            return OperationResponse(
                status=OperationStatusEnum.FAILED,
                payment_method=payment_method,
                type=OperationTypeEnum.CONFIRM,
                error_message=f"Invalid status {block_response.status}",
            )

        # Create PaymentOperation with the outcome
        self.payment_operation_repository.add(
            payment_method=payment_method,
            type=OperationTypeEnum.CONFIRM,
            status=block_response.status,
        )

        # Return Response
        return OperationResponse(
            status=block_response.status,
            payment_method=payment_method,
            type=OperationTypeEnum.CONFIRM,
            error_message=block_response.error_message,
        )

    @payment_operation_type
    @refresh_payment_method
    def after_confirm(self, payment_method: "protocols.AbstractPaymentMethod") -> "protocols.AbstractOperationResponse":
        # Verify that the payment can go through this operation type
        if not dl.can_after_confirm(payment_method):
            return OperationResponse(
                status=OperationStatusEnum.FAILED,
                payment_method=None,
                error_message="PaymentMethod cannot go through this operation",
                type=OperationTypeEnum.AFTER_CONFIRM,
            )

        # Create Started PaymentOperation
        self.payment_operation_repository.add(
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
        self.payment_operation_repository.add(
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
