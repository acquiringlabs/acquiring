from django_acquiring.protocols.enums import OperationStatusEnum, OperationTypeEnum
from django_acquiring.protocols.payments import AbstractPaymentMethod


def can_initialize(payment_method: AbstractPaymentMethod) -> bool:
    """
    Return whether the payment_method can go through the initialize operation.

    >>> from datetime import datetime
    >>> from django_acquiring.domain import PaymentMethod
    >>> payment_method = PaymentMethod(
    ...     id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     payment_attempt_id="200d03a9-8ac1-489d-894a-54af6de20823",
    ...     created_at=datetime.now(),
    ...     confirmable=True,
    ... )
    >>> can_initialize(payment_method)
    True

    A Payment Method that has already started initialized cannot go through initialize.
    >>> from django_acquiring.domain import PaymentOperation
    >>> from django_acquiring.protocols.enums import OperationTypeEnum, OperationStatusEnum
    >>> payment_operation_initialized_started = PaymentOperation(
    ...     payment_method_id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     type=OperationTypeEnum.initialize,
    ...     status=OperationStatusEnum.started,
    ... )
    >>> payment_method = PaymentMethod(
    ...     id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     payment_attempt_id="200d03a9-8ac1-489d-894a-54af6de20823",
    ...     created_at=datetime.now(),
    ...     confirmable=True,
    ...     payment_operations=[payment_operation_initialized_started],
    ... )
    >>> can_initialize(payment_method)
    False

    A Payment Method that has already completed initialized cannot go through initialize.
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
    >>> payment_method = PaymentMethod(
    ...     id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     payment_attempt_id="200d03a9-8ac1-489d-894a-54af6de20823",
    ...     created_at=datetime.now(),
    ...     confirmable=True,
    ...     payment_operations=[payment_operation_initialized_started, payment_operation_initialized_completed],
    ... )
    >>> can_initialize(payment_method)
    False

    A Payment Method that has already failed initialized cannot go through initialize.
    >>> from django_acquiring.domain import PaymentOperation
    >>> from django_acquiring.protocols.enums import OperationTypeEnum, OperationStatusEnum
    >>> payment_operation_initialized_started = PaymentOperation(
    ...     payment_method_id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     type=OperationTypeEnum.initialize,
    ...     status=OperationStatusEnum.started,
    ... )
    >>> payment_operation_initialized_failed = PaymentOperation(
    ...     payment_method_id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     type=OperationTypeEnum.initialize,
    ...     status=OperationStatusEnum.failed,
    ... )
    >>> payment_method = PaymentMethod(
    ...     id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     payment_attempt_id="200d03a9-8ac1-489d-894a-54af6de20823",
    ...     created_at=datetime.now(),
    ...     confirmable=True,
    ...     payment_operations=[payment_operation_initialized_started, payment_operation_initialized_failed],
    ... )
    >>> can_initialize(payment_method)
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


def can_process_actions(payment_method: AbstractPaymentMethod) -> bool:
    """
    Return whether the payment_method can go through the process_actions operation.

    A Payment Method that has already started initialization and ended requiring actions can go through,
    >>> from datetime import datetime
    >>> from django_acquiring.domain import PaymentMethod
    >>> from django_acquiring.domain import PaymentOperation
    >>> payment_operation_initialized_started = PaymentOperation(
    ...     payment_method_id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     type=OperationTypeEnum.initialize,
    ...     status=OperationStatusEnum.started,
    ... )
    >>> payment_operation_initialized_requires_action = PaymentOperation(
    ...     payment_method_id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     type=OperationTypeEnum.initialize,
    ...     status=OperationStatusEnum.requires_action,
    ... )
    >>> payment_method = PaymentMethod(
    ...     id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     payment_attempt_id="200d03a9-8ac1-489d-894a-54af6de20823",
    ...     created_at=datetime.now(),
    ...     confirmable=True,
    ...     payment_operations=[payment_operation_initialized_started, payment_operation_initialized_requires_action],
    ... )
    >>> can_process_actions(payment_method)
    True

    A Payment Method that has already started process_actions cannot go through process_actions.
    >>> from django_acquiring.domain import PaymentOperation
    >>> from django_acquiring.protocols.enums import OperationTypeEnum, OperationStatusEnum
    >>> payment_operation_process_actions_started = PaymentOperation(
    ...     payment_method_id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     type=OperationTypeEnum.process_actions,
    ...     status=OperationStatusEnum.started,
    ... )
    >>> payment_method = PaymentMethod(
    ...     id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     payment_attempt_id="200d03a9-8ac1-489d-894a-54af6de20823",
    ...     created_at=datetime.now(),
    ...     confirmable=True,
    ...     payment_operations=[payment_operation_process_actions_started],
    ... )
    >>> can_process_actions(payment_method)
    False

    A Payment Method that has started initialized but has not finished with require action
    cannot go through process_actions.
    >>> from django_acquiring.domain import PaymentOperation
    >>> from django_acquiring.protocols.enums import OperationTypeEnum, OperationStatusEnum
    >>> payment_operation_initialized_started = PaymentOperation(
    ...     payment_method_id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     type=OperationTypeEnum.initialize,
    ...     status=OperationStatusEnum.started,
    ... )
    >>> payment_method = PaymentMethod(
    ...     id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     payment_attempt_id="200d03a9-8ac1-489d-894a-54af6de20823",
    ...     created_at=datetime.now(),
    ...     confirmable=True,
    ...     payment_operations=[payment_operation_initialized_started],
    ... )
    >>> can_process_actions(payment_method)
    False

    A Payment Method that doesn't have an initialized that requires actions cannot go through process_actions.
    >>> from datetime import datetime
    >>> from django_acquiring.domain import PaymentMethod
    >>> payment_method = PaymentMethod(
    ...     id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     payment_attempt_id="200d03a9-8ac1-489d-894a-54af6de20823",
    ...     created_at=datetime.now(),
    ...     confirmable=True,
    ... )
    >>> can_process_actions(payment_method)
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


def can_pay(payment_method: AbstractPaymentMethod) -> bool:
    """
    Return whether the payment_method can go through the pay operation.

    A Payment Method that has already started initialization and ended requiring actions can go through,
    >>> from datetime import datetime
    >>> from django_acquiring.domain import PaymentMethod
    >>> from django_acquiring.domain import PaymentOperation
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
    >>> payment_method = PaymentMethod(
    ...     id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     payment_attempt_id="200d03a9-8ac1-489d-894a-54af6de20823",
    ...     created_at=datetime.now(),
    ...     confirmable=True,
    ...     payment_operations=[payment_operation_initialized_started, payment_operation_initialized_completed],
    ... )
    >>> can_pay(payment_method)
    True

    A Payment Method that has started initialization but hasn't completed it cannot go through
    >>> from datetime import datetime
    >>> from django_acquiring.domain import PaymentMethod
    >>> from django_acquiring.domain import PaymentOperation
    >>> payment_operation_initialized_started = PaymentOperation(
    ...     payment_method_id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     type=OperationTypeEnum.initialize,
    ...     status=OperationStatusEnum.started,
    ... )
    >>> payment_method = PaymentMethod(
    ...     id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     payment_attempt_id="200d03a9-8ac1-489d-894a-54af6de20823",
    ...     created_at=datetime.now(),
    ...     confirmable=True,
    ...     payment_operations=[payment_operation_initialized_started],
    ... )
    >>> can_pay(payment_method)
    False

    A Payment Method that has started initialization and has required actions but hasn't completed process_actions
    cannot go through.
    >>> from datetime import datetime
    >>> from django_acquiring.domain import PaymentMethod
    >>> from django_acquiring.domain import PaymentOperation
    >>> payment_operation_initialized_started = PaymentOperation(
    ...     payment_method_id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     type=OperationTypeEnum.initialize,
    ...     status=OperationStatusEnum.started,
    ... )
    >>> payment_operation_initialized_required_actions = PaymentOperation(
    ...     payment_method_id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     type=OperationTypeEnum.initialize,
    ...     status=OperationStatusEnum.requires_action,
    ... )
    >>> payment_method = PaymentMethod(
    ...     id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     payment_attempt_id="200d03a9-8ac1-489d-894a-54af6de20823",
    ...     created_at=datetime.now(),
    ...     confirmable=True,
    ...     payment_operations=[payment_operation_initialized_started, payment_operation_initialized_required_actions],
    ... )
    >>> can_pay(payment_method)
    False

    A Payment Method that has started initialization and has required actions and has completed process_actions
    can go through.
    >>> from datetime import datetime
    >>> from django_acquiring.domain import PaymentMethod
    >>> from django_acquiring.domain import PaymentOperation
    >>> payment_operation_initialized_started = PaymentOperation(
    ...     payment_method_id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     type=OperationTypeEnum.initialize,
    ...     status=OperationStatusEnum.started,
    ... )
    >>> payment_operation_initialized_required_actions = PaymentOperation(
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
    >>> payment_method = PaymentMethod(
    ...     id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     payment_attempt_id="200d03a9-8ac1-489d-894a-54af6de20823",
    ...     created_at=datetime.now(),
    ...     confirmable=True,
    ...     payment_operations=[
    ...         payment_operation_initialized_started,
    ...         payment_operation_initialized_required_actions,
    ...         payment_operation_process_actions_started,
    ...         payment_operation_process_actions_completed,
    ...     ],
    ... )
    >>> can_pay(payment_method)
    True

    A Payment Method that has started pay cannot go through.

    >>> from datetime import datetime
    >>> from django_acquiring.domain import PaymentMethod
    >>> from django_acquiring.domain import PaymentOperation
    >>> payment_operation_initialized_started = PaymentOperation(
    ...     payment_method_id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     type=OperationTypeEnum.initialize,
    ...     status=OperationStatusEnum.started,
    ... )
    >>> payment_operation_initialized_required_actions = PaymentOperation(
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
    >>> payment_method = PaymentMethod(
    ...     id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     payment_attempt_id="200d03a9-8ac1-489d-894a-54af6de20823",
    ...     created_at=datetime.now(),
    ...     confirmable=True,
    ...     payment_operations=[
    ...         payment_operation_initialized_started,
    ...         payment_operation_initialized_required_actions,
    ...         payment_operation_process_actions_started,
    ...         payment_operation_process_actions_completed,
    ...         payment_operation_pay_started,
    ...     ],
    ... )

    >>> can_pay(payment_method)
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


def can_after_pay(payment_method: AbstractPaymentMethod) -> bool:
    """
    Return whether the payment_method can go through the after pay operation.

    A Payment Method that has already initialized and has already pay can go through.
    >>> from datetime import datetime
    >>> from django_acquiring.domain import PaymentMethod
    >>> from django_acquiring.domain import PaymentOperation
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
    >>> payment_method = PaymentMethod(
    ...     id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     payment_attempt_id="200d03a9-8ac1-489d-894a-54af6de20823",
    ...     created_at=datetime.now(),
    ...     confirmable=True,
    ...     payment_operations=[
    ...         payment_operation_initialized_started,
    ...         payment_operation_initialized_completed,
    ...         payment_operation_pay_started,
    ...         payment_operation_pay_completed,
    ...     ],
    ... )
    >>> can_after_pay(payment_method)
    True

    A Payment Method that has not completed initialization cannot go through
    >>> from datetime import datetime
    >>> from django_acquiring.domain import PaymentMethod
    >>> from django_acquiring.domain import PaymentOperation
    >>> payment_operation_initialized_started = PaymentOperation(
    ...     payment_method_id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     type=OperationTypeEnum.initialize,
    ...     status=OperationStatusEnum.started,
    ... )
    >>> payment_method = PaymentMethod(
    ...     id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     payment_attempt_id="200d03a9-8ac1-489d-894a-54af6de20823",
    ...     created_at=datetime.now(),
    ...     confirmable=True,
    ...     payment_operations=[
    ...         payment_operation_initialized_started,
    ...     ],
    ... )
    >>> can_after_pay(payment_method)
    False

    A Payment Method that has not completed pay cannot go through
    >>> from datetime import datetime
    >>> from django_acquiring.domain import PaymentMethod
    >>> from django_acquiring.domain import PaymentOperation
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
    >>> payment_operation_pay_started = PaymentOperation(
    ...     payment_method_id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     type=OperationTypeEnum.pay,
    ...     status=OperationStatusEnum.started,
    ... )
    >>> payment_method = PaymentMethod(
    ...     id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     payment_attempt_id="200d03a9-8ac1-489d-894a-54af6de20823",
    ...     created_at=datetime.now(),
    ...     confirmable=True,
    ...     payment_operations=[
    ...         payment_operation_initialized_started,
    ...         payment_operation_initialized_completed,
    ...         payment_operation_pay_started,
    ...     ],
    ... )
    >>> can_after_pay(payment_method)
    False

    A Payment Method that has already started after pay cannot go through
    >>> from datetime import datetime
    >>> from django_acquiring.domain import PaymentMethod
    >>> from django_acquiring.domain import PaymentOperation
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
    >>> payment_method = PaymentMethod(
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
    ... )
    >>> can_after_pay(payment_method)
    False
    """
    if payment_method.has_payment_operation(
        type=OperationTypeEnum.after_pay,
        status=OperationStatusEnum.started,
    ):
        return False
    if can_initialize(payment_method) or can_pay(payment_method):
        return False

    if payment_method.has_payment_operation(
        type=OperationTypeEnum.initialize,
        status=OperationStatusEnum.started,
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


def can_confirm(payment_method: AbstractPaymentMethod) -> bool:
    """
    Return whether the payment_method can go through the confirm operation.

    A Payment Method that is confirmable and has completed pay can go through.
    >>> from datetime import datetime
    >>> from django_acquiring.domain import PaymentMethod
    >>> from django_acquiring.domain import PaymentOperation
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
    >>> payment_method = PaymentMethod(
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
    ... )
    >>> can_confirm(payment_method)
    True

    A Payment Method that is not confirmable cannot go through.
    >>> from datetime import datetime
    >>> from django_acquiring.domain import PaymentMethod
    >>> from django_acquiring.domain import PaymentOperation
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
    >>> payment_method = PaymentMethod(
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
    ... )
    >>> can_confirm(payment_method)
    False

    A Payment Method that has not completed payment cannot go through.
    >>> from datetime import datetime
    >>> from django_acquiring.domain import PaymentMethod
    >>> from django_acquiring.domain import PaymentOperation
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
    >>> payment_method = PaymentMethod(
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
    ...     ],
    ... )
    >>> can_confirm(payment_method)
    False

    A Payment Method that has started confirm cannot go through
    >>> from datetime import datetime
    >>> from django_acquiring.domain import PaymentMethod
    >>> from django_acquiring.domain import PaymentOperation
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
    >>> payment_method = PaymentMethod(
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
    ... )
    >>> can_confirm(payment_method)
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


def can_after_confirm(payment_method: AbstractPaymentMethod) -> bool:
    """
    Return whether the payment_method can go through the after confirm operation.

    A Payment Method that has already initialized and has already pay and has already confirmed can go through.
    >>> from datetime import datetime
    >>> from django_acquiring.domain import PaymentMethod
    >>> from django_acquiring.domain import PaymentOperation
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
    >>> payment_method = PaymentMethod(
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
    ... )
    >>> can_after_confirm(payment_method)
    True

    A Payment Method that has not completed initialization cannot go through
    >>> from datetime import datetime
    >>> from django_acquiring.domain import PaymentMethod
    >>> from django_acquiring.domain import PaymentOperation
    >>> payment_operation_initialized_started = PaymentOperation(
    ...     payment_method_id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     type=OperationTypeEnum.initialize,
    ...     status=OperationStatusEnum.started,
    ... )
    >>> payment_method = PaymentMethod(
    ...     id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     payment_attempt_id="200d03a9-8ac1-489d-894a-54af6de20823",
    ...     created_at=datetime.now(),
    ...     confirmable=True,
    ...     payment_operations=[
    ...         payment_operation_initialized_started,
    ...     ],
    ... )
    >>> can_after_confirm(payment_method)
    False

    A Payment Method that has not completed pay cannot go through
    >>> from datetime import datetime
    >>> from django_acquiring.domain import PaymentMethod
    >>> from django_acquiring.domain import PaymentOperation
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
    >>> payment_operation_pay_started = PaymentOperation(
    ...     payment_method_id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     type=OperationTypeEnum.pay,
    ...     status=OperationStatusEnum.started,
    ... )
    >>> payment_method = PaymentMethod(
    ...     id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     payment_attempt_id="200d03a9-8ac1-489d-894a-54af6de20823",
    ...     created_at=datetime.now(),
    ...     confirmable=True,
    ...     payment_operations=[
    ...         payment_operation_initialized_started,
    ...         payment_operation_initialized_completed,
    ...         payment_operation_pay_started,
    ...     ],
    ... )
    >>> can_after_confirm(payment_method)
    False

    A Payment Method that has already started after pay cannot go through
    >>> from datetime import datetime
    >>> from django_acquiring.domain import PaymentMethod
    >>> from django_acquiring.domain import PaymentOperation
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
    >>> payment_method = PaymentMethod(
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
    ... )
    >>> can_after_confirm(payment_method)
    False

    A Payment Method that has not completed confirm cannot go through
    >>> from datetime import datetime
    >>> from django_acquiring.domain import PaymentMethod
    >>> from django_acquiring.domain import PaymentOperation
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
    >>> payment_method = PaymentMethod(
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
    ... )
    >>> can_after_confirm(payment_method)
    False

    A Payment Method that has started after_confirm cannot go through
    >>> from datetime import datetime
    >>> from django_acquiring.domain import PaymentMethod
    >>> from django_acquiring.domain import PaymentOperation
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
    >>> payment_method = PaymentMethod(
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
    ... )
    >>> can_after_confirm(payment_method)
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
