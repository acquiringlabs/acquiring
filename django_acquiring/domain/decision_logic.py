from typing import TYPE_CHECKING

from django_acquiring.enums import OperationStatusEnum, OperationTypeEnum

if TYPE_CHECKING:
    from django_acquiring import protocols


def can_initialize(payment_method: "protocols.AbstractPaymentMethod") -> bool:
    """
    Return whether the payment_method can go through the initialize operation.

    First, we instantiate everything we need
    >>> from datetime import datetime
    >>> from django_acquiring.domain import PaymentMethod
    >>> from django_acquiring.domain import PaymentOperation
    >>> from django_acquiring.enums import OperationTypeEnum, OperationStatusEnum
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

    A Payment Method that has no payment operations can go through initialize.
    >>> can_initialize(PaymentMethod(
    ...     id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     payment_attempt_id="200d03a9-8ac1-489d-894a-54af6de20823",
    ...     created_at=datetime.now(),
    ...     confirmable=True,
    ... ))
    True

    A Payment Method that has already started initialized cannot go through initialize.
    >>> can_initialize(PaymentMethod(
    ...     id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     payment_attempt_id="200d03a9-8ac1-489d-894a-54af6de20823",
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
    ...     payment_attempt_id="200d03a9-8ac1-489d-894a-54af6de20823",
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
    ...     payment_attempt_id="200d03a9-8ac1-489d-894a-54af6de20823",
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
    ...     payment_attempt_id="200d03a9-8ac1-489d-894a-54af6de20823",
    ...     created_at=datetime.now(),
    ...     confirmable=True,
    ...     payment_operations=[
    ...         payment_operation_initialized_started,
    ...         payment_operation_initialized_requires_action,
    ...     ],
    ... ))
    False
    """
    if payment_method.has_payment_operation(type=OperationTypeEnum.INITIALIZE, status=OperationStatusEnum.STARTED):
        return False

    # If initialization already finished, it cannot go through initialize again
    if payment_method.has_payment_operation(
        type=OperationTypeEnum.INITIALIZE,
        status=OperationStatusEnum.COMPLETED,
    ) or payment_method.has_payment_operation(
        type=OperationTypeEnum.INITIALIZE,
        status=OperationStatusEnum.FAILED,
    ):
        return False

    return True


def can_process_action(payment_method: "protocols.AbstractPaymentMethod") -> bool:
    """
    Return whether the payment_method can go through the process_action operation.

    First, we instantiate everything we need
    >>> from datetime import datetime
    >>> from django_acquiring.domain import PaymentMethod
    >>> from django_acquiring.domain import PaymentOperation
    >>> from django_acquiring.enums import OperationTypeEnum, OperationStatusEnum
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
    >>> payment_operation_process_action_started = PaymentOperation(
    ...     payment_method_id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     type=OperationTypeEnum.PROCESS_ACTION,
    ...     status=OperationStatusEnum.STARTED,
    ... )

    A Payment Method that has already started initialization and ended requiring actions can go through,
    >>> can_process_action(PaymentMethod(
    ...     id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     payment_attempt_id="200d03a9-8ac1-489d-894a-54af6de20823",
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
    ...     payment_attempt_id="200d03a9-8ac1-489d-894a-54af6de20823",
    ...     created_at=datetime.now(),
    ...     confirmable=True,
    ...     payment_operations=[
    ...         payment_operation_initialized_started,
    ...         payment_operation_initialized_requires_action,
    ...         payment_operation_process_action_started,
    ...     ],
    ... ))
    False

    A Payment Method that has started initialized but failed
    cannot go through process_action.
    >>> can_process_action(PaymentMethod(
    ...     id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     payment_attempt_id="200d03a9-8ac1-489d-894a-54af6de20823",
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

    # Unless Payment Method initialized and required action, it cannot go through process_action
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


def can_pay(payment_method: "protocols.AbstractPaymentMethod") -> bool:
    """
    Return whether the payment_method can go through the pay operation.

    First, we instantiate everything we need
    >>> from datetime import datetime
    >>> from django_acquiring.domain import PaymentMethod
    >>> from django_acquiring.domain import PaymentOperation
    >>> from django_acquiring.enums import OperationTypeEnum, OperationStatusEnum
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

    A Payment Method that has already started initialization and completed it can go through pay.
    >>> can_pay(PaymentMethod(
    ...     id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     payment_attempt_id="200d03a9-8ac1-489d-894a-54af6de20823",
    ...     created_at=datetime.now(),
    ...     confirmable=True,
    ...     payment_operations=[
    ...         payment_operation_initialized_started,
    ...         payment_operation_initialized_completed,
    ...     ],
    ... ))
    True

    A Payment Method that has started initialization but hasn't completed it cannot go through
    >>> can_pay(PaymentMethod(
    ...     id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     payment_attempt_id="200d03a9-8ac1-489d-894a-54af6de20823",
    ...     created_at=datetime.now(),
    ...     confirmable=True,
    ...     payment_operations=[
    ...         payment_operation_initialized_started,
    ...     ],
    ... ))
    False

    A Payment Method that has started initialization and has required actions but hasn't completed process_action
    cannot go through.
    >>> can_pay(PaymentMethod(
    ...     id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     payment_attempt_id="200d03a9-8ac1-489d-894a-54af6de20823",
    ...     created_at=datetime.now(),
    ...     confirmable=True,
    ...     payment_operations=[
    ...         payment_operation_initialized_started,
    ...         payment_operation_initialized_requires_action,
    ...     ],
    ... ))
    False

    A Payment Method that has started initialization and has required actions and has completed process_action
    can go through.
    >>> can_pay(PaymentMethod(
    ...     id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     payment_attempt_id="200d03a9-8ac1-489d-894a-54af6de20823",
    ...     created_at=datetime.now(),
    ...     confirmable=True,
    ...     payment_operations=[
    ...         payment_operation_initialized_started,
    ...         payment_operation_initialized_requires_action,
    ...         payment_operation_process_action_started,
    ...         payment_operation_process_action_completed,
    ...     ],
    ... ))
    True

    A Payment Method that has started pay cannot go through.
    >>> can_pay(PaymentMethod(
    ...     id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     payment_attempt_id="200d03a9-8ac1-489d-894a-54af6de20823",
    ...     created_at=datetime.now(),
    ...     confirmable=True,
    ...     payment_operations=[
    ...         payment_operation_initialized_started,
    ...         payment_operation_initialized_requires_action,
    ...         payment_operation_process_action_started,
    ...         payment_operation_process_action_completed,
    ...         payment_operation_pay_started,
    ...     ],
    ... ))
    False
    """
    if can_initialize(payment_method) or can_process_action(payment_method):
        return False

    if payment_method.has_payment_operation(
        type=OperationTypeEnum.PAY,
        status=OperationStatusEnum.STARTED,
    ):
        return False

    if payment_method.has_payment_operation(
        type=OperationTypeEnum.INITIALIZE,
        status=OperationStatusEnum.STARTED,
    ):
        if payment_method.has_payment_operation(
            type=OperationTypeEnum.INITIALIZE,
            status=OperationStatusEnum.REQUIRES_ACTION,
        ):
            return payment_method.has_payment_operation(
                type=OperationTypeEnum.PROCESS_ACTION,
                status=OperationStatusEnum.COMPLETED,
            )
        if not payment_method.has_payment_operation(
            type=OperationTypeEnum.INITIALIZE,
            status=OperationStatusEnum.COMPLETED,
        ):
            return False

    return True


def can_after_pay(payment_method: "protocols.AbstractPaymentMethod") -> bool:
    """
    Return whether the payment_method can go through the after pay operation.

    First, we instantiate everything we need
    >>> from datetime import datetime
    >>> from django_acquiring.domain import PaymentMethod
    >>> from django_acquiring.domain import PaymentOperation
    >>> from django_acquiring.enums import OperationTypeEnum, OperationStatusEnum
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

    A Payment Method that has already initialized and has already pay can go through.
    >>> can_after_pay(PaymentMethod(
    ...     id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     payment_attempt_id="200d03a9-8ac1-489d-894a-54af6de20823",
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

    A Payment Method that has not completed initialization cannot go through
    >>> can_after_pay(PaymentMethod(
    ...     id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     payment_attempt_id="200d03a9-8ac1-489d-894a-54af6de20823",
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
    ...     payment_attempt_id="200d03a9-8ac1-489d-894a-54af6de20823",
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
    ...     payment_attempt_id="200d03a9-8ac1-489d-894a-54af6de20823",
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
    if can_initialize(payment_method) or can_process_action(payment_method) or can_pay(payment_method):
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
        ) and not payment_method.has_payment_operation(
            type=OperationTypeEnum.INITIALIZE,
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
    >>> from django_acquiring.domain import PaymentMethod
    >>> from django_acquiring.domain import PaymentOperation
    >>> from django_acquiring.enums import OperationTypeEnum, OperationStatusEnum
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

    A Payment Method that is confirmable and has completed pay can go through.
    >>> can_confirm(PaymentMethod(
    ...     id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     payment_attempt_id="200d03a9-8ac1-489d-894a-54af6de20823",
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

    A Payment Method that is not confirmable cannot go through.
    >>> can_confirm(PaymentMethod(
    ...     id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     payment_attempt_id="200d03a9-8ac1-489d-894a-54af6de20823",
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
    ...     payment_attempt_id="200d03a9-8ac1-489d-894a-54af6de20823",
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
    ...     payment_attempt_id="200d03a9-8ac1-489d-894a-54af6de20823",
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
            can_pay(payment_method),
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
    >>> from django_acquiring.domain import PaymentMethod
    >>> from django_acquiring.domain import PaymentOperation
    >>> from django_acquiring.enums import OperationTypeEnum, OperationStatusEnum
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

    A Payment Method that has already initialized and has already pay and has already confirmed can go through.
    >>> can_after_confirm(PaymentMethod(
    ...     id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     payment_attempt_id="200d03a9-8ac1-489d-894a-54af6de20823",
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

    A Payment Method that has not completed initialization cannot go through
    >>> can_after_confirm(PaymentMethod(
    ...     id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     payment_attempt_id="200d03a9-8ac1-489d-894a-54af6de20823",
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
    ...     payment_attempt_id="200d03a9-8ac1-489d-894a-54af6de20823",
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
    ...     payment_attempt_id="200d03a9-8ac1-489d-894a-54af6de20823",
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
    ...     payment_attempt_id="200d03a9-8ac1-489d-894a-54af6de20823",
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
    ...     payment_attempt_id="200d03a9-8ac1-489d-894a-54af6de20823",
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
            can_pay(payment_method),
            can_after_pay(payment_method),
            can_confirm(payment_method),
        ]
    ):
        return False

    if not payment_method.confirmable:
        return False

    if not payment_method.has_payment_operation(
        type=OperationTypeEnum.INITIALIZE,
        status=OperationStatusEnum.COMPLETED,
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
