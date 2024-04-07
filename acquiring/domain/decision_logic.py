from typing import TYPE_CHECKING

from acquiring.enums import OperationStatusEnum, OperationTypeEnum

if TYPE_CHECKING:
    from acquiring import protocols


# TODO Test these functions with hypothesis


def can_initialize(payment_method: "protocols.AbstractPaymentMethod") -> bool:
    """
    Return whether the payment_method can go through the initialize operation.

    First, we instantiate everything we need
    >>> from datetime import datetime
    >>> from acquiring.domain import PaymentMethod
    >>> from acquiring.domain import PaymentAttempt
    >>> from acquiring.domain import PaymentOperation
    >>> from acquiring.enums import OperationTypeEnum, OperationStatusEnum
    >>> payment_operation_initialized_started = PaymentOperation(
    ...     payment_method_id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     type=OperationTypeEnum.INITIALIZE,
    ...     status=OperationStatusEnum.STARTED,
    ... )
    >>> payment_operation_initialized_completed = PaymentOperation(
    ...     payment_method_id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     type=OperationTypeEnum.INITIALIZE,
    ...     status=OperationStatusEnum.COMPLETED,
    ... )
    >>> payment_operation_initialized_failed = PaymentOperation(
    ...     payment_method_id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     type=OperationTypeEnum.INITIALIZE,
    ...     status=OperationStatusEnum.FAILED,
    ... )
    >>> payment_operation_initialized_requires_action = PaymentOperation(
    ...     payment_method_id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     type=OperationTypeEnum.INITIALIZE,
    ...     status=OperationStatusEnum.REQUIRES_ACTION,
    ... )
    >>> payment_operation_initialized_not_performed = PaymentOperation(
    ...     payment_method_id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     type=OperationTypeEnum.INITIALIZE,
    ...     status=OperationStatusEnum.NOT_PERFORMED,
    ... )
    >>> payment_attempt = PaymentAttempt(
    ...     id="612a66aa-a133-4585-8866-977b08ecc05f",
    ...     created_at=datetime.now(),
    ...     amount=10,
    ...     currency="USD",
    ...     payment_method_ids=[],
    ... )

    A Payment Method that has no payment operations can go through initialize.
    >>> can_initialize(PaymentMethod(
    ...     id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     payment_attempt=payment_attempt,
    ...     created_at=datetime.now(),
    ...     confirmable=True,
    ... ))
    True

    A Payment Method that has already started initialized cannot go through initialize.
    >>> can_initialize(PaymentMethod(
    ...     id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     payment_attempt=payment_attempt,
    ...     created_at=datetime.now(),
    ...     confirmable=True,
    ...     payment_operations=[
    ...         payment_operation_initialized_started,
    ...     ],
    ... ))
    False

    A Payment Method that has already completed initialized cannot go through initialize.
    >>> can_initialize(PaymentMethod(
    ...     id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     payment_attempt=payment_attempt,
    ...     created_at=datetime.now(),
    ...     confirmable=True,
    ...     payment_operations=[
    ...         payment_operation_initialized_started,
    ...         payment_operation_initialized_completed,
    ...     ],
    ... ))
    False

    A Payment Method that has already failed initialized cannot go through initialize.
    >>> can_initialize(PaymentMethod(
    ...     id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     payment_attempt=payment_attempt,
    ...     created_at=datetime.now(),
    ...     confirmable=True,
    ...     payment_operations=[
    ...         payment_operation_initialized_started,
    ...         payment_operation_initialized_failed,
    ...     ],
    ... ))
    False

    A Payment Method that has already finished initialized requiring actions cannot go through initialize.
    >>> can_initialize(PaymentMethod(
    ...     id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     payment_attempt=payment_attempt,
    ...     created_at=datetime.now(),
    ...     confirmable=True,
    ...     payment_operations=[
    ...         payment_operation_initialized_started,
    ...         payment_operation_initialized_requires_action,
    ...     ],
    ... ))
    False

    A Payment Method that has not performed initialize requiring actions cannot go through initialize.
    >>> can_initialize(PaymentMethod(
    ...     id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     payment_attempt=payment_attempt,
    ...     created_at=datetime.now(),
    ...     confirmable=True,
    ...     payment_operations=[
    ...         payment_operation_initialized_started,
    ...         payment_operation_initialized_not_performed,
    ...     ],
    ... ))
    False
    """
    if payment_method.has_payment_operation(type=OperationTypeEnum.INITIALIZE, status=OperationStatusEnum.STARTED):
        return False

    return True


def can_process_action(payment_method: "protocols.AbstractPaymentMethod") -> bool:
    """
    Return whether the payment_method can go through the process_action operation.

    First, we instantiate everything we need
    >>> from datetime import datetime
    >>> from acquiring.domain import PaymentMethod
    >>> from acquiring.domain import PaymentAttempt
    >>> from acquiring.domain import PaymentOperation
    >>> from acquiring.enums import OperationTypeEnum, OperationStatusEnum
    >>> payment_operation_initialized_started = PaymentOperation(
    ...     payment_method_id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     type=OperationTypeEnum.INITIALIZE,
    ...     status=OperationStatusEnum.STARTED,
    ... )
    >>> payment_operation_initialized_completed = PaymentOperation(
    ...     payment_method_id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     type=OperationTypeEnum.INITIALIZE,
    ...     status=OperationStatusEnum.COMPLETED,
    ... )
    >>> payment_operation_initialized_failed = PaymentOperation(
    ...     payment_method_id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     type=OperationTypeEnum.INITIALIZE,
    ...     status=OperationStatusEnum.FAILED,
    ... )
    >>> payment_operation_initialized_requires_action = PaymentOperation(
    ...     payment_method_id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     type=OperationTypeEnum.INITIALIZE,
    ...     status=OperationStatusEnum.REQUIRES_ACTION,
    ... )
    >>> payment_operation_initialized_not_performed = PaymentOperation(
    ...     payment_method_id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     type=OperationTypeEnum.INITIALIZE,
    ...     status=OperationStatusEnum.NOT_PERFORMED,
    ... )
    >>> payment_operation_process_action_started = PaymentOperation(
    ...     payment_method_id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     type=OperationTypeEnum.PROCESS_ACTION,
    ...     status=OperationStatusEnum.STARTED,
    ... )
    >>> payment_attempt = PaymentAttempt(
    ...     id="612a66aa-a133-4585-8866-977b08ecc05f",
    ...     created_at=datetime.now(),
    ...     amount=10,
    ...     currency="USD",
    ...     payment_method_ids=[],
    ... )

    A Payment Method that has already started initialization and ended requiring actions can go through,
    >>> can_process_action(PaymentMethod(
    ...     id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     payment_attempt=payment_attempt,
    ...     created_at=datetime.now(),
    ...     confirmable=True,
    ...     payment_operations=[
    ...         payment_operation_initialized_started,
    ...         payment_operation_initialized_requires_action,
    ...     ],
    ... ))
    True

    A Payment Method that has already started process_action cannot go through process_action.
    >>> can_process_action(PaymentMethod(
    ...     id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     payment_attempt=payment_attempt,
    ...     created_at=datetime.now(),
    ...     confirmable=True,
    ...     payment_operations=[
    ...         payment_operation_initialized_started,
    ...         payment_operation_initialized_requires_action,
    ...         payment_operation_process_action_started,
    ...     ],
    ... ))
    False

    A Payment Method that has not performed initialize cannot go through process_action.
    >>> can_process_action(PaymentMethod(
    ...     id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     payment_attempt=payment_attempt,
    ...     created_at=datetime.now(),
    ...     confirmable=True,
    ...     payment_operations=[
    ...         payment_operation_initialized_started,
    ...         payment_operation_initialized_not_performed,
    ...     ],
    ... ))
    False

    A Payment Method that has started initialized but failed
    cannot go through process_action.
    >>> can_process_action(PaymentMethod(
    ...     id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     payment_attempt=payment_attempt,
    ...     created_at=datetime.now(),
    ...     confirmable=True,
    ...     payment_operations=[
    ...         payment_operation_initialized_started,
    ...         payment_operation_initialized_failed,
    ...     ],
    ... ))
    False
    """
    if payment_method.has_payment_operation(
        type=OperationTypeEnum.PROCESS_ACTION,
        status=OperationStatusEnum.STARTED,
    ):
        return False

    if not (
        payment_method.has_payment_operation(
            type=OperationTypeEnum.INITIALIZE,
            status=OperationStatusEnum.STARTED,
        )
        and payment_method.has_payment_operation(
            type=OperationTypeEnum.INITIALIZE,
            status=OperationStatusEnum.REQUIRES_ACTION,
        )
    ):
        return False

    return True


def can_after_pay(payment_method: "protocols.AbstractPaymentMethod") -> bool:
    """
    Return whether the payment_method can go through the after pay operation.

    First, we instantiate everything we need
    >>> from datetime import datetime
    >>> from acquiring.domain import PaymentMethod
    >>> from acquiring.domain import PaymentAttempt
    >>> from acquiring.domain import PaymentOperation
    >>> from acquiring.enums import OperationTypeEnum, OperationStatusEnum
    >>> payment_operation_initialized_started = PaymentOperation(
    ...     payment_method_id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     type=OperationTypeEnum.INITIALIZE,
    ...     status=OperationStatusEnum.STARTED,
    ... )
    >>> payment_operation_initialized_completed = PaymentOperation(
    ...     payment_method_id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     type=OperationTypeEnum.INITIALIZE,
    ...     status=OperationStatusEnum.COMPLETED,
    ... )
    >>> payment_operation_initialized_failed = PaymentOperation(
    ...     payment_method_id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     type=OperationTypeEnum.INITIALIZE,
    ...     status=OperationStatusEnum.FAILED,
    ... )
    >>> payment_operation_initialized_requires_action = PaymentOperation(
    ...     payment_method_id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     type=OperationTypeEnum.INITIALIZE,
    ...     status=OperationStatusEnum.REQUIRES_ACTION,
    ... )
    >>> payment_operation_initialized_not_performed = PaymentOperation(
    ...     payment_method_id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     type=OperationTypeEnum.INITIALIZE,
    ...     status=OperationStatusEnum.NOT_PERFORMED,
    ... )
    >>> payment_operation_process_action_started = PaymentOperation(
    ...     payment_method_id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     type=OperationTypeEnum.PROCESS_ACTION,
    ...     status=OperationStatusEnum.STARTED,
    ... )
    >>> payment_operation_process_action_completed = PaymentOperation(
    ...     payment_method_id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     type=OperationTypeEnum.PROCESS_ACTION,
    ...     status=OperationStatusEnum.COMPLETED,
    ... )
    >>> payment_operation_pay_started = PaymentOperation(
    ...     payment_method_id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     type=OperationTypeEnum.PAY,
    ...     status=OperationStatusEnum.STARTED,
    ... )
    >>> payment_operation_pay_completed = PaymentOperation(
    ...     payment_method_id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     type=OperationTypeEnum.PAY,
    ...     status=OperationStatusEnum.COMPLETED,
    ... )
    >>> payment_operation_after_pay_started = PaymentOperation(
    ...     payment_method_id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     type=OperationTypeEnum.AFTER_PAY,
    ...     status=OperationStatusEnum.STARTED,
    ... )
    >>> payment_attempt = PaymentAttempt(
    ...     id="612a66aa-a133-4585-8866-977b08ecc05f",
    ...     created_at=datetime.now(),
    ...     amount=10,
    ...     currency="USD",
    ...     payment_method_ids=[],
    ... )

    A Payment Method that has already initialized and has already pay can go through.
    >>> can_after_pay(PaymentMethod(
    ...     id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     payment_attempt=payment_attempt,
    ...     created_at=datetime.now(),
    ...     confirmable=True,
    ...     payment_operations=[
    ...         payment_operation_initialized_started,
    ...         payment_operation_initialized_requires_action,
    ...         payment_operation_process_action_started,
    ...         payment_operation_process_action_completed,
    ...         payment_operation_pay_started,
    ...         payment_operation_pay_completed,
    ...     ],
    ... ))
    True

    A Payment Method that has not performed initialized and has already pay can go through.
    >>> can_after_pay(PaymentMethod(
    ...     id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     payment_attempt=payment_attempt,
    ...     created_at=datetime.now(),
    ...     confirmable=True,
    ...     payment_operations=[
    ...         payment_operation_initialized_started,
    ...         payment_operation_initialized_not_performed,
    ...         payment_operation_pay_started,
    ...         payment_operation_pay_completed,
    ...     ],
    ... ))
    True

    A Payment Method that has not completed initialization cannot go through
    >>> can_after_pay(PaymentMethod(
    ...     id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     payment_attempt=payment_attempt,
    ...     created_at=datetime.now(),
    ...     confirmable=True,
    ...     payment_operations=[
    ...         payment_operation_initialized_started,
    ...     ],
    ... ))
    False

    A Payment Method that has not completed pay cannot go through
    >>> can_after_pay(PaymentMethod(
    ...     id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     payment_attempt=payment_attempt,
    ...     created_at=datetime.now(),
    ...     confirmable=True,
    ...     payment_operations=[
    ...         payment_operation_initialized_started,
    ...         payment_operation_initialized_completed,
    ...         payment_operation_pay_started,
    ...     ],
    ... ))
    False

    A Payment Method that has already started after pay cannot go through
    >>> can_after_pay(PaymentMethod(
    ...     id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     payment_attempt=payment_attempt,
    ...     created_at=datetime.now(),
    ...     confirmable=True,
    ...     payment_operations=[
    ...         payment_operation_initialized_started,
    ...         payment_operation_initialized_completed,
    ...         payment_operation_pay_started,
    ...         payment_operation_pay_completed,
    ...         payment_operation_after_pay_started,
    ...     ],
    ... ))
    False
    """
    if payment_method.has_payment_operation(
        type=OperationTypeEnum.AFTER_PAY,
        status=OperationStatusEnum.STARTED,
    ):
        return False

    if any([can_initialize(payment_method), can_process_action(payment_method)]):
        return False

    if payment_method.has_payment_operation(
        type=OperationTypeEnum.INITIALIZE,
        status=OperationStatusEnum.STARTED,
    ):
        if payment_method.has_payment_operation(
            type=OperationTypeEnum.INITIALIZE,
            status=OperationStatusEnum.REQUIRES_ACTION,
        ) and not payment_method.has_payment_operation(
            type=OperationTypeEnum.PROCESS_ACTION,
            status=OperationStatusEnum.COMPLETED,
        ):
            return False
        elif not payment_method.has_payment_operation(
            type=OperationTypeEnum.INITIALIZE,
            status=OperationStatusEnum.REQUIRES_ACTION,
        ) and not any(
            [
                payment_method.has_payment_operation(
                    type=OperationTypeEnum.INITIALIZE,
                    status=OperationStatusEnum.COMPLETED,
                ),
                payment_method.has_payment_operation(
                    type=OperationTypeEnum.INITIALIZE,
                    status=OperationStatusEnum.NOT_PERFORMED,
                ),
            ]
        ):
            return False

    if payment_method.has_payment_operation(
        type=OperationTypeEnum.PAY,
        status=OperationStatusEnum.STARTED,
    ) and not payment_method.has_payment_operation(
        type=OperationTypeEnum.PAY,
        status=OperationStatusEnum.COMPLETED,
    ):
        return False

    if payment_method.has_payment_operation(
        type=OperationTypeEnum.PAY,
        status=OperationStatusEnum.STARTED,
    ) and not payment_method.has_payment_operation(
        type=OperationTypeEnum.PAY,
        status=OperationStatusEnum.COMPLETED,
    ):
        return False

    return True


def can_confirm(payment_method: "protocols.AbstractPaymentMethod") -> bool:
    """
    Return whether the payment_method can go through the confirm operation.

    First, we instantiate everything we need
    >>> from datetime import datetime
    >>> from acquiring.domain import PaymentMethod
    >>> from acquiring.domain import PaymentAttempt
    >>> from acquiring.domain import PaymentOperation
    >>> from acquiring.enums import OperationTypeEnum, OperationStatusEnum
    >>> payment_operation_initialized_started = PaymentOperation(
    ...     payment_method_id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     type=OperationTypeEnum.INITIALIZE,
    ...     status=OperationStatusEnum.STARTED,
    ... )
    >>> payment_operation_initialized_completed = PaymentOperation(
    ...     payment_method_id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     type=OperationTypeEnum.INITIALIZE,
    ...     status=OperationStatusEnum.COMPLETED,
    ... )
    >>> payment_operation_initialized_failed = PaymentOperation(
    ...     payment_method_id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     type=OperationTypeEnum.INITIALIZE,
    ...     status=OperationStatusEnum.FAILED,
    ... )
    >>> payment_operation_initialized_requires_action = PaymentOperation(
    ...     payment_method_id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     type=OperationTypeEnum.INITIALIZE,
    ...     status=OperationStatusEnum.REQUIRES_ACTION,
    ... )
    >>> payment_operation_initialized_not_performed = PaymentOperation(
    ...     payment_method_id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     type=OperationTypeEnum.INITIALIZE,
    ...     status=OperationStatusEnum.NOT_PERFORMED,
    ... )
    >>> payment_operation_process_action_started = PaymentOperation(
    ...     payment_method_id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     type=OperationTypeEnum.PROCESS_ACTION,
    ...     status=OperationStatusEnum.STARTED,
    ... )
    >>> payment_operation_process_action_completed = PaymentOperation(
    ...     payment_method_id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     type=OperationTypeEnum.PROCESS_ACTION,
    ...     status=OperationStatusEnum.COMPLETED,
    ... )
    >>> payment_operation_pay_started = PaymentOperation(
    ...     payment_method_id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     type=OperationTypeEnum.PAY,
    ...     status=OperationStatusEnum.STARTED,
    ... )
    >>> payment_operation_pay_completed = PaymentOperation(
    ...     payment_method_id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     type=OperationTypeEnum.PAY,
    ...     status=OperationStatusEnum.COMPLETED,
    ... )
    >>> payment_operation_after_pay_started = PaymentOperation(
    ...     payment_method_id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     type=OperationTypeEnum.AFTER_PAY,
    ...     status=OperationStatusEnum.STARTED,
    ... )
    >>> payment_operation_after_pay_completed = PaymentOperation(
    ...     payment_method_id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     type=OperationTypeEnum.AFTER_PAY,
    ...     status=OperationStatusEnum.COMPLETED,
    ... )
    >>> payment_operation_confirm_started = PaymentOperation(
    ...     payment_method_id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     type=OperationTypeEnum.CONFIRM,
    ...     status=OperationStatusEnum.STARTED,
    ... )
    >>> payment_attempt = PaymentAttempt(
    ...     id="612a66aa-a133-4585-8866-977b08ecc05f",
    ...     created_at=datetime.now(),
    ...     amount=10,
    ...     currency="USD",
    ...     payment_method_ids=[],
    ... )

    A Payment Method that is confirmable and has completed pay can go through.
    >>> can_confirm(PaymentMethod(
    ...     id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     payment_attempt=payment_attempt,
    ...     created_at=datetime.now(),
    ...     confirmable=True,
    ...     payment_operations=[
    ...         payment_operation_initialized_started,
    ...         payment_operation_initialized_completed,
    ...         payment_operation_pay_started,
    ...         payment_operation_pay_completed,
    ...         payment_operation_after_pay_started,
    ...         payment_operation_after_pay_completed,
    ...     ],
    ... ))
    True

    A Payment Method that is confirmable and has not completed initialize, then pay can go through.
    >>> can_confirm(PaymentMethod(
    ...     id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     payment_attempt=payment_attempt,
    ...     created_at=datetime.now(),
    ...     confirmable=True,
    ...     payment_operations=[
    ...         payment_operation_initialized_started,
    ...         payment_operation_initialized_not_performed,
    ...         payment_operation_pay_started,
    ...         payment_operation_pay_completed,
    ...         payment_operation_after_pay_started,
    ...         payment_operation_after_pay_completed,
    ...     ],
    ... ))
    True

    A Payment Method that is not confirmable cannot go through.
    >>> can_confirm(PaymentMethod(
    ...     id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     payment_attempt=payment_attempt,
    ...     created_at=datetime.now(),
    ...     confirmable=False,
    ...     payment_operations=[
    ...         payment_operation_initialized_started,
    ...         payment_operation_initialized_completed,
    ...         payment_operation_pay_started,
    ...         payment_operation_pay_completed,
    ...         payment_operation_after_pay_started,
    ...         payment_operation_after_pay_completed,
    ...     ],
    ... ))
    False

    A Payment Method that has not completed payment cannot go through.
    >>> can_confirm(PaymentMethod(
    ...     id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     payment_attempt=payment_attempt,
    ...     created_at=datetime.now(),
    ...     confirmable=True,
    ...     payment_operations=[
    ...         payment_operation_initialized_started,
    ...         payment_operation_initialized_completed,
    ...         payment_operation_pay_started,
    ...         payment_operation_pay_completed,
    ...         payment_operation_after_pay_started,
    ...     ],
    ... ))
    False

    A Payment Method that has started confirm cannot go through
    >>> can_confirm(PaymentMethod(
    ...     id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     payment_attempt=payment_attempt,
    ...     created_at=datetime.now(),
    ...     confirmable=True,
    ...     payment_operations=[
    ...         payment_operation_initialized_started,
    ...         payment_operation_initialized_completed,
    ...         payment_operation_pay_started,
    ...         payment_operation_pay_completed,
    ...         payment_operation_after_pay_started,
    ...         payment_operation_after_pay_completed,
    ...         payment_operation_confirm_started,
    ...     ],
    ... ))
    False
    """
    if payment_method.confirmable is False:
        return False

    if any(
        [
            can_initialize(payment_method),
            can_process_action(payment_method),
            can_after_pay(payment_method),
        ]
    ):
        return False

    if not payment_method.has_payment_operation(
        type=OperationTypeEnum.AFTER_PAY,
        status=OperationStatusEnum.COMPLETED,
    ):
        return False

    if payment_method.has_payment_operation(
        type=OperationTypeEnum.CONFIRM,
        status=OperationStatusEnum.STARTED,
    ):
        return False

    return True


def can_after_confirm(payment_method: "protocols.AbstractPaymentMethod") -> bool:
    """
    Return whether the payment_method can go through the after confirm operation.

    >>> from datetime import datetime
    >>> from acquiring.domain import PaymentMethod
    >>> from acquiring.domain import PaymentAttempt
    >>> from acquiring.domain import PaymentOperation
    >>> from acquiring.enums import OperationTypeEnum, OperationStatusEnum
    >>> payment_operation_initialized_started = PaymentOperation(
    ...     payment_method_id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     type=OperationTypeEnum.INITIALIZE,
    ...     status=OperationStatusEnum.STARTED,
    ... )
    >>> payment_operation_initialized_completed = PaymentOperation(
    ...     payment_method_id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     type=OperationTypeEnum.INITIALIZE,
    ...     status=OperationStatusEnum.COMPLETED,
    ... )
    >>> payment_operation_initialized_failed = PaymentOperation(
    ...     payment_method_id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     type=OperationTypeEnum.INITIALIZE,
    ...     status=OperationStatusEnum.FAILED,
    ... )
    >>> payment_operation_initialized_requires_action = PaymentOperation(
    ...     payment_method_id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     type=OperationTypeEnum.INITIALIZE,
    ...     status=OperationStatusEnum.REQUIRES_ACTION,
    ... )
    >>> payment_operation_initialized_not_performed = PaymentOperation(
    ...     payment_method_id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     type=OperationTypeEnum.INITIALIZE,
    ...     status=OperationStatusEnum.NOT_PERFORMED,
    ... )
    >>> payment_operation_process_action_started = PaymentOperation(
    ...     payment_method_id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     type=OperationTypeEnum.PROCESS_ACTION,
    ...     status=OperationStatusEnum.STARTED,
    ... )
    >>> payment_operation_process_action_completed = PaymentOperation(
    ...     payment_method_id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     type=OperationTypeEnum.PROCESS_ACTION,
    ...     status=OperationStatusEnum.COMPLETED,
    ... )
    >>> payment_operation_pay_started = PaymentOperation(
    ...     payment_method_id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     type=OperationTypeEnum.PAY,
    ...     status=OperationStatusEnum.STARTED,
    ... )
    >>> payment_operation_pay_completed = PaymentOperation(
    ...     payment_method_id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     type=OperationTypeEnum.PAY,
    ...     status=OperationStatusEnum.COMPLETED,
    ... )
    >>> payment_operation_after_pay_started = PaymentOperation(
    ...     payment_method_id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     type=OperationTypeEnum.AFTER_PAY,
    ...     status=OperationStatusEnum.STARTED,
    ... )
    >>> payment_operation_after_pay_completed = PaymentOperation(
    ...     payment_method_id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     type=OperationTypeEnum.AFTER_PAY,
    ...     status=OperationStatusEnum.COMPLETED,
    ... )
    >>> payment_operation_confirm_started = PaymentOperation(
    ...     payment_method_id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     type=OperationTypeEnum.CONFIRM,
    ...     status=OperationStatusEnum.STARTED,
    ... )
    >>> payment_operation_confirm_completed = PaymentOperation(
    ...     payment_method_id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     type=OperationTypeEnum.CONFIRM,
    ...     status=OperationStatusEnum.COMPLETED,
    ... )
    >>> payment_operation_after_confirm_started = PaymentOperation(
    ...     payment_method_id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     type=OperationTypeEnum.AFTER_CONFIRM,
    ...     status=OperationStatusEnum.STARTED,
    ... )
    >>> payment_attempt = PaymentAttempt(
    ...     id="612a66aa-a133-4585-8866-977b08ecc05f",
    ...     created_at=datetime.now(),
    ...     amount=10,
    ...     currency="USD",
    ...     payment_method_ids=[],
    ... )

    A Payment Method that has already initialized and has already pay and has already confirmed can go through.
    >>> can_after_confirm(PaymentMethod(
    ...     id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     payment_attempt=payment_attempt,
    ...     created_at=datetime.now(),
    ...     confirmable=True,
    ...     payment_operations=[
    ...         payment_operation_initialized_started,
    ...         payment_operation_initialized_completed,
    ...         payment_operation_pay_started,
    ...         payment_operation_pay_completed,
    ...         payment_operation_after_pay_started,
    ...         payment_operation_after_pay_completed,
    ...         payment_operation_confirm_started,
    ...         payment_operation_confirm_completed,
    ...     ],
    ... ))
    True

    A Payment Method that has not performed initialized and has already pay and has already confirmed can go through.
    >>> can_after_confirm(PaymentMethod(
    ...     id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     payment_attempt=payment_attempt,
    ...     created_at=datetime.now(),
    ...     confirmable=True,
    ...     payment_operations=[
    ...         payment_operation_initialized_started,
    ...         payment_operation_initialized_not_performed,
    ...         payment_operation_pay_started,
    ...         payment_operation_pay_completed,
    ...         payment_operation_after_pay_started,
    ...         payment_operation_after_pay_completed,
    ...         payment_operation_confirm_started,
    ...         payment_operation_confirm_completed,
    ...     ],
    ... ))
    True

    A Payment Method that has not completed initialization cannot go through
    >>> can_after_confirm(PaymentMethod(
    ...     id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     payment_attempt=payment_attempt,
    ...     created_at=datetime.now(),
    ...     confirmable=True,
    ...     payment_operations=[
    ...         payment_operation_initialized_started,
    ...     ],
    ... ))
    False

    A Payment Method that has not completed pay cannot go through
    >>> can_after_confirm(PaymentMethod(
    ...     id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     payment_attempt=payment_attempt,
    ...     created_at=datetime.now(),
    ...     confirmable=True,
    ...     payment_operations=[
    ...         payment_operation_initialized_started,
    ...         payment_operation_initialized_completed,
    ...         payment_operation_pay_started,
    ...     ],
    ... ))
    False

    A Payment Method that has already started after pay cannot go through
    >>> can_after_confirm(PaymentMethod(
    ...     id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     payment_attempt=payment_attempt,
    ...     created_at=datetime.now(),
    ...     confirmable=True,
    ...     payment_operations=[
    ...         payment_operation_initialized_started,
    ...         payment_operation_initialized_completed,
    ...         payment_operation_pay_started,
    ...         payment_operation_pay_completed,
    ...         payment_operation_after_pay_started,
    ...     ],
    ... ))
    False

    A Payment Method that has not completed confirm cannot go through
    >>> can_after_confirm(PaymentMethod(
    ...     id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     payment_attempt=payment_attempt,
    ...     created_at=datetime.now(),
    ...     confirmable=True,
    ...     payment_operations=[
    ...         payment_operation_initialized_started,
    ...         payment_operation_initialized_completed,
    ...         payment_operation_pay_started,
    ...         payment_operation_pay_completed,
    ...         payment_operation_after_pay_started,
    ...         payment_operation_confirm_started,
    ...     ],
    ... ))
    False

    A Payment Method that has started after_confirm cannot go through
    >>> can_after_confirm(PaymentMethod(
    ...     id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     payment_attempt=payment_attempt,
    ...     created_at=datetime.now(),
    ...     confirmable=True,
    ...     payment_operations=[
    ...         payment_operation_initialized_started,
    ...         payment_operation_initialized_completed,
    ...         payment_operation_pay_started,
    ...         payment_operation_pay_completed,
    ...         payment_operation_after_pay_started,
    ...         payment_operation_after_pay_completed,
    ...         payment_operation_confirm_started,
    ...         payment_operation_confirm_completed,
    ...         payment_operation_after_confirm_started,
    ...     ],
    ... ))
    False
    """
    if any(
        [
            can_initialize(payment_method),
            can_process_action(payment_method),
            can_after_pay(payment_method),
            can_confirm(payment_method),
        ]
    ):
        return False

    if not payment_method.confirmable:
        return False

    if not any(
        [
            payment_method.has_payment_operation(
                type=OperationTypeEnum.INITIALIZE,
                status=OperationStatusEnum.COMPLETED,
            ),
            payment_method.has_payment_operation(
                type=OperationTypeEnum.INITIALIZE,
                status=OperationStatusEnum.NOT_PERFORMED,
            ),
        ]
    ):
        return False

    if payment_method.has_payment_operation(
        type=OperationTypeEnum.INITIALIZE,
        status=OperationStatusEnum.REQUIRES_ACTION,
    ) and not payment_method.has_payment_operation(
        type=OperationTypeEnum.PROCESS_ACTION,
        status=OperationStatusEnum.COMPLETED,
    ):
        return False

    if not payment_method.has_payment_operation(
        type=OperationTypeEnum.PAY,
        status=OperationStatusEnum.COMPLETED,
    ):
        return False

    if not payment_method.has_payment_operation(
        type=OperationTypeEnum.AFTER_PAY,
        status=OperationStatusEnum.COMPLETED,
    ):
        return False

    if not payment_method.has_payment_operation(
        type=OperationTypeEnum.CONFIRM,
        status=OperationStatusEnum.COMPLETED,
    ):
        return False

    if payment_method.has_payment_operation(
        type=OperationTypeEnum.AFTER_CONFIRM,
        status=OperationStatusEnum.STARTED,
    ):
        return False

    return True
