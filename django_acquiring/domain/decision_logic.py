from typing import TYPE_CHECKING

from django_acquiring.protocols.enums import OperationStatusEnum, OperationTypeEnum

if TYPE_CHECKING:
    from django_acquiring.protocols.payments import AbstractPaymentMethod


def can_initialize(payment_method: "AbstractPaymentMethod") -> bool:
    """
    Return whether the payment_method can go through the initialize operation.

    First, we instantiate everything we need
    >>> from datetime import datetime
    >>> from django_acquiring.domain import PaymentMethod
    >>> from django_acquiring.domain import PaymentOperation
    >>> from django_acquiring.protocols.enums import OperationTypeEnum, OperationStatusEnum
    >>> payment_operation_initialized_started = PaymentOperation(
    ...     payment_method_id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     type=OperationTypeEnum.initialize,
    ...     status=OperationStatusEnum.started,
    ... )
    >>> payment_operation_initialized_completed = PaymentOperation(
    ...     payment_method_id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     type=OperationTypeEnum.initialize,
    ...     status=OperationStatusEnum.completed,
    ... )
    >>> payment_operation_initialized_failed = PaymentOperation(
    ...     payment_method_id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     type=OperationTypeEnum.initialize,
    ...     status=OperationStatusEnum.failed,
    ... )
    >>> payment_operation_initialized_requires_action = PaymentOperation(
    ...     payment_method_id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     type=OperationTypeEnum.initialize,
    ...     status=OperationStatusEnum.requires_action,
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
    if payment_method.has_payment_operation(type=OperationTypeEnum.initialize, status=OperationStatusEnum.started):
        return False

    # If initialization already finished, it cannot go through initialize again
    if payment_method.has_payment_operation(
        type=OperationTypeEnum.initialize,
        status=OperationStatusEnum.completed,
    ) or payment_method.has_payment_operation(
        type=OperationTypeEnum.initialize,
        status=OperationStatusEnum.failed,
    ):
        return False

    return True


def can_process_actions(payment_method: "AbstractPaymentMethod") -> bool:
    """
    Return whether the payment_method can go through the process_actions operation.

    First, we instantiate everything we need
    >>> from datetime import datetime
    >>> from django_acquiring.domain import PaymentMethod
    >>> from django_acquiring.domain import PaymentOperation
    >>> from django_acquiring.protocols.enums import OperationTypeEnum, OperationStatusEnum
    >>> payment_operation_initialized_started = PaymentOperation(
    ...     payment_method_id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     type=OperationTypeEnum.initialize,
    ...     status=OperationStatusEnum.started,
    ... )
    >>> payment_operation_initialized_completed = PaymentOperation(
    ...     payment_method_id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     type=OperationTypeEnum.initialize,
    ...     status=OperationStatusEnum.completed,
    ... )
    >>> payment_operation_initialized_failed = PaymentOperation(
    ...     payment_method_id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     type=OperationTypeEnum.initialize,
    ...     status=OperationStatusEnum.failed,
    ... )
    >>> payment_operation_initialized_requires_action = PaymentOperation(
    ...     payment_method_id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     type=OperationTypeEnum.initialize,
    ...     status=OperationStatusEnum.requires_action,
    ... )
    >>> payment_operation_process_actions_started = PaymentOperation(
    ...     payment_method_id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     type=OperationTypeEnum.process_actions,
    ...     status=OperationStatusEnum.started,
    ... )

    A Payment Method that has already started initialization and ended requiring actions can go through,
    >>> can_process_actions(PaymentMethod(
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

    A Payment Method that has already started process_actions cannot go through process_actions.
    >>> can_process_actions(PaymentMethod(
    ...     id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     payment_attempt_id="200d03a9-8ac1-489d-894a-54af6de20823",
    ...     created_at=datetime.now(),
    ...     confirmable=True,
    ...     payment_operations=[
    ...         payment_operation_initialized_started,
    ...         payment_operation_initialized_requires_action,
    ...         payment_operation_process_actions_started,
    ...     ],
    ... ))
    False

    A Payment Method that has started initialized but failed
    cannot go through process_actions.
    >>> can_process_actions(PaymentMethod(
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
        type=OperationTypeEnum.process_actions,
        status=OperationStatusEnum.started,
    ):
        return False

    # Unless Payment Method initialized and required action, it cannot go through process_actions
    if not (
        payment_method.has_payment_operation(
            type=OperationTypeEnum.initialize,
            status=OperationStatusEnum.started,
        )
        and payment_method.has_payment_operation(
            type=OperationTypeEnum.initialize,
            status=OperationStatusEnum.requires_action,
        )
    ):
        return False

    return True


def can_pay(payment_method: "AbstractPaymentMethod") -> bool:
    """
    Return whether the payment_method can go through the pay operation.

    First, we instantiate everything we need
    >>> from datetime import datetime
    >>> from django_acquiring.domain import PaymentMethod
    >>> from django_acquiring.domain import PaymentOperation
    >>> from django_acquiring.protocols.enums import OperationTypeEnum, OperationStatusEnum
    >>> payment_operation_initialized_started = PaymentOperation(
    ...     payment_method_id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     type=OperationTypeEnum.initialize,
    ...     status=OperationStatusEnum.started,
    ... )
    >>> payment_operation_initialized_completed = PaymentOperation(
    ...     payment_method_id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     type=OperationTypeEnum.initialize,
    ...     status=OperationStatusEnum.completed,
    ... )
    >>> payment_operation_initialized_failed = PaymentOperation(
    ...     payment_method_id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     type=OperationTypeEnum.initialize,
    ...     status=OperationStatusEnum.failed,
    ... )
    >>> payment_operation_initialized_requires_action = PaymentOperation(
    ...     payment_method_id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     type=OperationTypeEnum.initialize,
    ...     status=OperationStatusEnum.requires_action,
    ... )
    >>> payment_operation_process_actions_started = PaymentOperation(
    ...     payment_method_id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     type=OperationTypeEnum.process_actions,
    ...     status=OperationStatusEnum.started,
    ... )
    >>> payment_operation_process_actions_completed = PaymentOperation(
    ...     payment_method_id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     type=OperationTypeEnum.process_actions,
    ...     status=OperationStatusEnum.completed,
    ... )
    >>> payment_operation_pay_started = PaymentOperation(
    ...     payment_method_id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     type=OperationTypeEnum.pay,
    ...     status=OperationStatusEnum.started,
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

    A Payment Method that has started initialization and has required actions but hasn't completed process_actions
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

    A Payment Method that has started initialization and has required actions and has completed process_actions
    can go through.
    >>> can_pay(PaymentMethod(
    ...     id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     payment_attempt_id="200d03a9-8ac1-489d-894a-54af6de20823",
    ...     created_at=datetime.now(),
    ...     confirmable=True,
    ...     payment_operations=[
    ...         payment_operation_initialized_started,
    ...         payment_operation_initialized_requires_action,
    ...         payment_operation_process_actions_started,
    ...         payment_operation_process_actions_completed,
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
    ...         payment_operation_process_actions_started,
    ...         payment_operation_process_actions_completed,
    ...         payment_operation_pay_started,
    ...     ],
    ... ))
    False
    """
    if can_initialize(payment_method) or can_process_actions(payment_method):
        return False

    if payment_method.has_payment_operation(
        type=OperationTypeEnum.pay,
        status=OperationStatusEnum.started,
    ):
        return False

    if payment_method.has_payment_operation(
        type=OperationTypeEnum.initialize,
        status=OperationStatusEnum.started,
    ):
        if payment_method.has_payment_operation(
            type=OperationTypeEnum.initialize,
            status=OperationStatusEnum.requires_action,
        ):
            return payment_method.has_payment_operation(
                type=OperationTypeEnum.process_actions,
                status=OperationStatusEnum.completed,
            )
        if not payment_method.has_payment_operation(
            type=OperationTypeEnum.initialize,
            status=OperationStatusEnum.completed,
        ):
            return False

    return True


def can_after_pay(payment_method: "AbstractPaymentMethod") -> bool:
    """
    Return whether the payment_method can go through the after pay operation.

    First, we instantiate everything we need
    >>> from datetime import datetime
    >>> from django_acquiring.domain import PaymentMethod
    >>> from django_acquiring.domain import PaymentOperation
    >>> from django_acquiring.protocols.enums import OperationTypeEnum, OperationStatusEnum
    >>> payment_operation_initialized_started = PaymentOperation(
    ...     payment_method_id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     type=OperationTypeEnum.initialize,
    ...     status=OperationStatusEnum.started,
    ... )
    >>> payment_operation_initialized_completed = PaymentOperation(
    ...     payment_method_id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     type=OperationTypeEnum.initialize,
    ...     status=OperationStatusEnum.completed,
    ... )
    >>> payment_operation_initialized_failed = PaymentOperation(
    ...     payment_method_id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     type=OperationTypeEnum.initialize,
    ...     status=OperationStatusEnum.failed,
    ... )
    >>> payment_operation_initialized_requires_action = PaymentOperation(
    ...     payment_method_id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     type=OperationTypeEnum.initialize,
    ...     status=OperationStatusEnum.requires_action,
    ... )
    >>> payment_operation_process_actions_started = PaymentOperation(
    ...     payment_method_id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     type=OperationTypeEnum.process_actions,
    ...     status=OperationStatusEnum.started,
    ... )
    >>> payment_operation_process_actions_completed = PaymentOperation(
    ...     payment_method_id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     type=OperationTypeEnum.process_actions,
    ...     status=OperationStatusEnum.completed,
    ... )
    >>> payment_operation_pay_started = PaymentOperation(
    ...     payment_method_id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     type=OperationTypeEnum.pay,
    ...     status=OperationStatusEnum.started,
    ... )
    >>> payment_operation_pay_completed = PaymentOperation(
    ...     payment_method_id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     type=OperationTypeEnum.pay,
    ...     status=OperationStatusEnum.completed,
    ... )
    >>> payment_operation_after_pay_started = PaymentOperation(
    ...     payment_method_id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     type=OperationTypeEnum.after_pay,
    ...     status=OperationStatusEnum.started,
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
    ...         payment_operation_process_actions_started,
    ...         payment_operation_process_actions_completed,
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
        type=OperationTypeEnum.after_pay,
        status=OperationStatusEnum.started,
    ):
        return False
    if can_initialize(payment_method) or can_process_actions(payment_method) or can_pay(payment_method):
        return False

    if payment_method.has_payment_operation(
        type=OperationTypeEnum.initialize,
        status=OperationStatusEnum.started,
    ):
        if payment_method.has_payment_operation(
            type=OperationTypeEnum.initialize,
            status=OperationStatusEnum.requires_action,
        ) and not payment_method.has_payment_operation(
            type=OperationTypeEnum.process_actions,
            status=OperationStatusEnum.completed,
        ):
            return False
        elif not payment_method.has_payment_operation(
            type=OperationTypeEnum.initialize,
            status=OperationStatusEnum.requires_action,
        ) and not payment_method.has_payment_operation(
            type=OperationTypeEnum.initialize,
            status=OperationStatusEnum.completed,
        ):
            return False

    if payment_method.has_payment_operation(
        type=OperationTypeEnum.pay,
        status=OperationStatusEnum.started,
    ) and not payment_method.has_payment_operation(
        type=OperationTypeEnum.pay,
        status=OperationStatusEnum.completed,
    ):
        return False

    if payment_method.has_payment_operation(
        type=OperationTypeEnum.pay,
        status=OperationStatusEnum.started,
    ) and not payment_method.has_payment_operation(
        type=OperationTypeEnum.pay,
        status=OperationStatusEnum.completed,
    ):
        return False

    return True


def can_confirm(payment_method: "AbstractPaymentMethod") -> bool:
    """
    Return whether the payment_method can go through the confirm operation.

    First, we instantiate everything we need
    >>> from datetime import datetime
    >>> from django_acquiring.domain import PaymentMethod
    >>> from django_acquiring.domain import PaymentOperation
    >>> from django_acquiring.protocols.enums import OperationTypeEnum, OperationStatusEnum
    >>> payment_operation_initialized_started = PaymentOperation(
    ...     payment_method_id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     type=OperationTypeEnum.initialize,
    ...     status=OperationStatusEnum.started,
    ... )
    >>> payment_operation_initialized_completed = PaymentOperation(
    ...     payment_method_id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     type=OperationTypeEnum.initialize,
    ...     status=OperationStatusEnum.completed,
    ... )
    >>> payment_operation_initialized_failed = PaymentOperation(
    ...     payment_method_id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     type=OperationTypeEnum.initialize,
    ...     status=OperationStatusEnum.failed,
    ... )
    >>> payment_operation_initialized_requires_action = PaymentOperation(
    ...     payment_method_id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     type=OperationTypeEnum.initialize,
    ...     status=OperationStatusEnum.requires_action,
    ... )
    >>> payment_operation_process_actions_started = PaymentOperation(
    ...     payment_method_id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     type=OperationTypeEnum.process_actions,
    ...     status=OperationStatusEnum.started,
    ... )
    >>> payment_operation_process_actions_completed = PaymentOperation(
    ...     payment_method_id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     type=OperationTypeEnum.process_actions,
    ...     status=OperationStatusEnum.completed,
    ... )
    >>> payment_operation_pay_started = PaymentOperation(
    ...     payment_method_id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     type=OperationTypeEnum.pay,
    ...     status=OperationStatusEnum.started,
    ... )
    >>> payment_operation_pay_completed = PaymentOperation(
    ...     payment_method_id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     type=OperationTypeEnum.pay,
    ...     status=OperationStatusEnum.completed,
    ... )
    >>> payment_operation_after_pay_started = PaymentOperation(
    ...     payment_method_id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     type=OperationTypeEnum.after_pay,
    ...     status=OperationStatusEnum.started,
    ... )
    >>> payment_operation_after_pay_completed = PaymentOperation(
    ...     payment_method_id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     type=OperationTypeEnum.after_pay,
    ...     status=OperationStatusEnum.completed,
    ... )
    >>> payment_operation_confirm_started = PaymentOperation(
    ...     payment_method_id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     type=OperationTypeEnum.confirm,
    ...     status=OperationStatusEnum.started,
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
            can_process_actions(payment_method),
            can_pay(payment_method),
            can_after_pay(payment_method),
        ]
    ):
        return False

    if not payment_method.has_payment_operation(
        type=OperationTypeEnum.after_pay,
        status=OperationStatusEnum.completed,
    ):
        return False

    if payment_method.has_payment_operation(
        type=OperationTypeEnum.confirm,
        status=OperationStatusEnum.started,
    ):
        return False

    return True


def can_after_confirm(payment_method: "AbstractPaymentMethod") -> bool:
    """
    Return whether the payment_method can go through the after confirm operation.

    >>> from datetime import datetime
    >>> from django_acquiring.domain import PaymentMethod
    >>> from django_acquiring.domain import PaymentOperation
    >>> from django_acquiring.protocols.enums import OperationTypeEnum, OperationStatusEnum
    >>> payment_operation_initialized_started = PaymentOperation(
    ...     payment_method_id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     type=OperationTypeEnum.initialize,
    ...     status=OperationStatusEnum.started,
    ... )
    >>> payment_operation_initialized_completed = PaymentOperation(
    ...     payment_method_id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     type=OperationTypeEnum.initialize,
    ...     status=OperationStatusEnum.completed,
    ... )
    >>> payment_operation_initialized_failed = PaymentOperation(
    ...     payment_method_id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     type=OperationTypeEnum.initialize,
    ...     status=OperationStatusEnum.failed,
    ... )
    >>> payment_operation_initialized_requires_action = PaymentOperation(
    ...     payment_method_id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     type=OperationTypeEnum.initialize,
    ...     status=OperationStatusEnum.requires_action,
    ... )
    >>> payment_operation_process_actions_started = PaymentOperation(
    ...     payment_method_id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     type=OperationTypeEnum.process_actions,
    ...     status=OperationStatusEnum.started,
    ... )
    >>> payment_operation_process_actions_completed = PaymentOperation(
    ...     payment_method_id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     type=OperationTypeEnum.process_actions,
    ...     status=OperationStatusEnum.completed,
    ... )
    >>> payment_operation_pay_started = PaymentOperation(
    ...     payment_method_id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     type=OperationTypeEnum.pay,
    ...     status=OperationStatusEnum.started,
    ... )
    >>> payment_operation_pay_completed = PaymentOperation(
    ...     payment_method_id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     type=OperationTypeEnum.pay,
    ...     status=OperationStatusEnum.completed,
    ... )
    >>> payment_operation_after_pay_started = PaymentOperation(
    ...     payment_method_id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     type=OperationTypeEnum.after_pay,
    ...     status=OperationStatusEnum.started,
    ... )
    >>> payment_operation_after_pay_completed = PaymentOperation(
    ...     payment_method_id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     type=OperationTypeEnum.after_pay,
    ...     status=OperationStatusEnum.completed,
    ... )
    >>> payment_operation_confirm_started = PaymentOperation(
    ...     payment_method_id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     type=OperationTypeEnum.confirm,
    ...     status=OperationStatusEnum.started,
    ... )
    >>> payment_operation_confirm_completed = PaymentOperation(
    ...     payment_method_id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     type=OperationTypeEnum.confirm,
    ...     status=OperationStatusEnum.completed,
    ... )
    >>> payment_operation_after_confirm_started = PaymentOperation(
    ...     payment_method_id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     type=OperationTypeEnum.after_confirm,
    ...     status=OperationStatusEnum.started,
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
            can_process_actions(payment_method),
            can_pay(payment_method),
            can_after_pay(payment_method),
            can_confirm(payment_method),
        ]
    ):
        return False

    if not payment_method.confirmable:
        return False

    if not payment_method.has_payment_operation(
        type=OperationTypeEnum.initialize,
        status=OperationStatusEnum.completed,
    ):
        return False

    if payment_method.has_payment_operation(
        type=OperationTypeEnum.initialize,
        status=OperationStatusEnum.requires_action,
    ) and not payment_method.has_payment_operation(
        type=OperationTypeEnum.process_actions,
        status=OperationStatusEnum.completed,
    ):
        return False

    if not payment_method.has_payment_operation(
        type=OperationTypeEnum.pay,
        status=OperationStatusEnum.completed,
    ):
        return False

    if not payment_method.has_payment_operation(
        type=OperationTypeEnum.after_pay,
        status=OperationStatusEnum.completed,
    ):
        return False

    if not payment_method.has_payment_operation(
        type=OperationTypeEnum.confirm,
        status=OperationStatusEnum.completed,
    ):
        return False

    if payment_method.has_payment_operation(
        type=OperationTypeEnum.after_confirm,
        status=OperationStatusEnum.started,
    ):
        return False

    return True
