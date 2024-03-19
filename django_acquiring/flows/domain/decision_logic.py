from django_acquiring.protocols.payments import (
    AbstractPaymentMethod,
    PaymentOperationStatusEnum,
    PaymentOperationTypeEnum,
)


def can_initialize(payment_method: AbstractPaymentMethod) -> bool:
    """
    Return whether the payment_method can go through the initialize operation.

    >>> from datetime import datetime
    >>> from django_acquiring.payments.domain import PaymentMethod
    >>> payment_method = PaymentMethod(
    ...     id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     payment_attempt_id="200d03a9-8ac1-489d-894a-54af6de20823",
    ...     created_at=datetime.now(),
    ...     confirmable=True,
    ... )
    >>> can_initialize(payment_method)
    True

    A Payment Method that has already started initialized cannot go through initialize.
    >>> from django_acquiring.payments.domain import PaymentOperation
    >>> from django_acquiring.protocols.payments import PaymentOperationTypeEnum, PaymentOperationStatusEnum
    >>> payment_operation_initialized_started = PaymentOperation(
    ...     payment_method_id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     type=PaymentOperationTypeEnum.initialize,
    ...     status=PaymentOperationStatusEnum.started,
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
    >>> from django_acquiring.payments.domain import PaymentOperation
    >>> from django_acquiring.protocols.payments import PaymentOperationTypeEnum, PaymentOperationStatusEnum
    >>> payment_operation_initialized_started = PaymentOperation(
    ...     payment_method_id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     type=PaymentOperationTypeEnum.initialize,
    ...     status=PaymentOperationStatusEnum.started,
    ... )
    >>> payment_operation_initialized_completed = PaymentOperation(
    ...     payment_method_id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     type=PaymentOperationTypeEnum.initialize,
    ...     status=PaymentOperationStatusEnum.completed,
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
    >>> from django_acquiring.payments.domain import PaymentOperation
    >>> from django_acquiring.protocols.payments import PaymentOperationTypeEnum, PaymentOperationStatusEnum
    >>> payment_operation_initialized_started = PaymentOperation(
    ...     payment_method_id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     type=PaymentOperationTypeEnum.initialize,
    ...     status=PaymentOperationStatusEnum.started,
    ... )
    >>> payment_operation_initialized_failed = PaymentOperation(
    ...     payment_method_id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     type=PaymentOperationTypeEnum.initialize,
    ...     status=PaymentOperationStatusEnum.failed,
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
    if payment_method.has_payment_operation(
        type=PaymentOperationTypeEnum.initialize, status=PaymentOperationStatusEnum.started
    ):
        return False

    # If initialization already finished, it cannot go through initialize again
    if payment_method.has_payment_operation(
        type=PaymentOperationTypeEnum.initialize,
        status=PaymentOperationStatusEnum.completed,
    ) or payment_method.has_payment_operation(
        type=PaymentOperationTypeEnum.initialize,
        status=PaymentOperationStatusEnum.failed,
    ):
        return False

    return True


def can_process_actions(payment_method: AbstractPaymentMethod) -> bool:
    """
    Return whether the payment_method can go through the process_actions operation.

    A Payment Method that has already started initialization and ended requiring actions can go through,
    >>> from datetime import datetime
    >>> from django_acquiring.payments.domain import PaymentMethod
    >>> from django_acquiring.payments.domain import PaymentOperation
    >>> payment_operation_initialized_started = PaymentOperation(
    ...     payment_method_id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     type=PaymentOperationTypeEnum.initialize,
    ...     status=PaymentOperationStatusEnum.started,
    ... )
    >>> payment_operation_initialized_requires_action = PaymentOperation(
    ...     payment_method_id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     type=PaymentOperationTypeEnum.initialize,
    ...     status=PaymentOperationStatusEnum.requires_action,
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
    >>> from django_acquiring.payments.domain import PaymentOperation
    >>> from django_acquiring.protocols.payments import PaymentOperationTypeEnum, PaymentOperationStatusEnum
    >>> payment_operation_process_actions_started = PaymentOperation(
    ...     payment_method_id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     type=PaymentOperationTypeEnum.process_actions,
    ...     status=PaymentOperationStatusEnum.started,
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
    >>> from django_acquiring.payments.domain import PaymentOperation
    >>> from django_acquiring.protocols.payments import PaymentOperationTypeEnum, PaymentOperationStatusEnum
    >>> payment_operation_initialized_started = PaymentOperation(
    ...     payment_method_id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     type=PaymentOperationTypeEnum.initialize,
    ...     status=PaymentOperationStatusEnum.started,
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
    >>> from django_acquiring.payments.domain import PaymentMethod
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
        type=PaymentOperationTypeEnum.process_actions,
        status=PaymentOperationStatusEnum.started,
    ):
        return False

    # Unless Payment Method initialized and required action, it cannot go through process_actions
    if not (
        payment_method.has_payment_operation(
            type=PaymentOperationTypeEnum.initialize,
            status=PaymentOperationStatusEnum.started,
        )
        and payment_method.has_payment_operation(
            type=PaymentOperationTypeEnum.initialize,
            status=PaymentOperationStatusEnum.requires_action,
        )
    ):
        return False

    return True


def can_pay(payment_method: AbstractPaymentMethod) -> bool:
    """
    Return whether the payment_method can go through the pay operation.

    A Payment Method that has already started initialization and ended requiring actions can go through,
    >>> from datetime import datetime
    >>> from django_acquiring.payments.domain import PaymentMethod
    >>> from django_acquiring.payments.domain import PaymentOperation
    >>> payment_operation_initialized_started = PaymentOperation(
    ...     payment_method_id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     type=PaymentOperationTypeEnum.initialize,
    ...     status=PaymentOperationStatusEnum.started,
    ... )
    >>> payment_operation_initialized_completed = PaymentOperation(
    ...     payment_method_id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     type=PaymentOperationTypeEnum.initialize,
    ...     status=PaymentOperationStatusEnum.completed,
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
    >>> from django_acquiring.payments.domain import PaymentMethod
    >>> from django_acquiring.payments.domain import PaymentOperation
    >>> payment_operation_initialized_started = PaymentOperation(
    ...     payment_method_id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     type=PaymentOperationTypeEnum.initialize,
    ...     status=PaymentOperationStatusEnum.started,
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
    >>> from django_acquiring.payments.domain import PaymentMethod
    >>> from django_acquiring.payments.domain import PaymentOperation
    >>> payment_operation_initialized_started = PaymentOperation(
    ...     payment_method_id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     type=PaymentOperationTypeEnum.initialize,
    ...     status=PaymentOperationStatusEnum.started,
    ... )
    >>> payment_operation_initialized_required_actions = PaymentOperation(
    ...     payment_method_id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     type=PaymentOperationTypeEnum.initialize,
    ...     status=PaymentOperationStatusEnum.requires_action,
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
    >>> from django_acquiring.payments.domain import PaymentMethod
    >>> from django_acquiring.payments.domain import PaymentOperation
    >>> payment_operation_initialized_started = PaymentOperation(
    ...     payment_method_id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     type=PaymentOperationTypeEnum.initialize,
    ...     status=PaymentOperationStatusEnum.started,
    ... )
    >>> payment_operation_initialized_required_actions = PaymentOperation(
    ...     payment_method_id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     type=PaymentOperationTypeEnum.initialize,
    ...     status=PaymentOperationStatusEnum.requires_action,
    ... )
    >>> payment_operation_process_actions_started = PaymentOperation(
    ...     payment_method_id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     type=PaymentOperationTypeEnum.process_actions,
    ...     status=PaymentOperationStatusEnum.started,
    ... )
    >>> payment_operation_process_actions_completed = PaymentOperation(
    ...     payment_method_id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     type=PaymentOperationTypeEnum.process_actions,
    ...     status=PaymentOperationStatusEnum.completed,
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
    >>> from django_acquiring.payments.domain import PaymentMethod
    >>> from django_acquiring.payments.domain import PaymentOperation
    >>> payment_operation_initialized_started = PaymentOperation(
    ...     payment_method_id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     type=PaymentOperationTypeEnum.initialize,
    ...     status=PaymentOperationStatusEnum.started,
    ... )
    >>> payment_operation_initialized_required_actions = PaymentOperation(
    ...     payment_method_id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     type=PaymentOperationTypeEnum.initialize,
    ...     status=PaymentOperationStatusEnum.requires_action,
    ... )
    >>> payment_operation_process_actions_started = PaymentOperation(
    ...     payment_method_id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     type=PaymentOperationTypeEnum.process_actions,
    ...     status=PaymentOperationStatusEnum.started,
    ... )
    >>> payment_operation_process_actions_completed = PaymentOperation(
    ...     payment_method_id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     type=PaymentOperationTypeEnum.process_actions,
    ...     status=PaymentOperationStatusEnum.completed,
    ... )
    >>> payment_operation_pay_started = PaymentOperation(
    ...     payment_method_id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     type=PaymentOperationTypeEnum.pay,
    ...     status=PaymentOperationStatusEnum.started,
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
        type=PaymentOperationTypeEnum.pay,
        status=PaymentOperationStatusEnum.started,
    ):
        return False

    if payment_method.has_payment_operation(
        type=PaymentOperationTypeEnum.initialize,
        status=PaymentOperationStatusEnum.started,
    ):
        if payment_method.has_payment_operation(
            type=PaymentOperationTypeEnum.initialize,
            status=PaymentOperationStatusEnum.requires_action,
        ):
            return payment_method.has_payment_operation(
                type=PaymentOperationTypeEnum.process_actions,
                status=PaymentOperationStatusEnum.completed,
            )
        if not payment_method.has_payment_operation(
            type=PaymentOperationTypeEnum.initialize,
            status=PaymentOperationStatusEnum.completed,
        ):
            return False

    return True


def can_after_pay(payment_method: AbstractPaymentMethod) -> bool:
    """
    Return whether the payment_method can go through the after pay operation.

    A Payment Method that has already initialized and has already pay can go through.
    >>> from datetime import datetime
    >>> from django_acquiring.payments.domain import PaymentMethod
    >>> from django_acquiring.payments.domain import PaymentOperation
    >>> payment_operation_initialized_started = PaymentOperation(
    ...     payment_method_id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     type=PaymentOperationTypeEnum.initialize,
    ...     status=PaymentOperationStatusEnum.started,
    ... )
    >>> payment_operation_initialized_completed = PaymentOperation(
    ...     payment_method_id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     type=PaymentOperationTypeEnum.initialize,
    ...     status=PaymentOperationStatusEnum.completed,
    ... )
    >>> payment_operation_pay_started = PaymentOperation(
    ...     payment_method_id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     type=PaymentOperationTypeEnum.pay,
    ...     status=PaymentOperationStatusEnum.started,
    ... )
    >>> payment_operation_pay_completed = PaymentOperation(
    ...     payment_method_id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     type=PaymentOperationTypeEnum.pay,
    ...     status=PaymentOperationStatusEnum.completed,
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
    >>> from django_acquiring.payments.domain import PaymentMethod
    >>> from django_acquiring.payments.domain import PaymentOperation
    >>> payment_operation_initialized_started = PaymentOperation(
    ...     payment_method_id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     type=PaymentOperationTypeEnum.initialize,
    ...     status=PaymentOperationStatusEnum.started,
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
    >>> from django_acquiring.payments.domain import PaymentMethod
    >>> from django_acquiring.payments.domain import PaymentOperation
    >>> payment_operation_initialized_started = PaymentOperation(
    ...     payment_method_id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     type=PaymentOperationTypeEnum.initialize,
    ...     status=PaymentOperationStatusEnum.started,
    ... )
    >>> payment_operation_initialized_completed = PaymentOperation(
    ...     payment_method_id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     type=PaymentOperationTypeEnum.initialize,
    ...     status=PaymentOperationStatusEnum.completed,
    ... )
    >>> payment_operation_pay_started = PaymentOperation(
    ...     payment_method_id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     type=PaymentOperationTypeEnum.pay,
    ...     status=PaymentOperationStatusEnum.started,
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
    >>> from django_acquiring.payments.domain import PaymentMethod
    >>> from django_acquiring.payments.domain import PaymentOperation
    >>> payment_operation_initialized_started = PaymentOperation(
    ...     payment_method_id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     type=PaymentOperationTypeEnum.initialize,
    ...     status=PaymentOperationStatusEnum.started,
    ... )
    >>> payment_operation_initialized_completed = PaymentOperation(
    ...     payment_method_id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     type=PaymentOperationTypeEnum.initialize,
    ...     status=PaymentOperationStatusEnum.completed,
    ... )
    >>> payment_operation_pay_started = PaymentOperation(
    ...     payment_method_id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     type=PaymentOperationTypeEnum.pay,
    ...     status=PaymentOperationStatusEnum.started,
    ... )
    >>> payment_operation_pay_completed = PaymentOperation(
    ...     payment_method_id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     type=PaymentOperationTypeEnum.pay,
    ...     status=PaymentOperationStatusEnum.completed,
    ... )
    >>> payment_operation_after_pay_started = PaymentOperation(
    ...     payment_method_id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     type=PaymentOperationTypeEnum.after_pay,
    ...     status=PaymentOperationStatusEnum.started,
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
        type=PaymentOperationTypeEnum.after_pay,
        status=PaymentOperationStatusEnum.started,
    ):
        return False
    if can_initialize(payment_method) or can_pay(payment_method):
        return False

    if payment_method.has_payment_operation(
        type=PaymentOperationTypeEnum.initialize,
        status=PaymentOperationStatusEnum.started,
    ) and not payment_method.has_payment_operation(
        type=PaymentOperationTypeEnum.initialize,
        status=PaymentOperationStatusEnum.completed,
    ):
        return False

    if payment_method.has_payment_operation(
        type=PaymentOperationTypeEnum.pay,
        status=PaymentOperationStatusEnum.started,
    ) and not payment_method.has_payment_operation(
        type=PaymentOperationTypeEnum.pay,
        status=PaymentOperationStatusEnum.completed,
    ):
        return False

    return True


def can_confirm(payment_method: AbstractPaymentMethod) -> bool:
    """
    Return whether the payment_method can go through the confirm operation.

    A Payment Method that is confirmable and has completed pay can go through.
    >>> from datetime import datetime
    >>> from django_acquiring.payments.domain import PaymentMethod
    >>> from django_acquiring.payments.domain import PaymentOperation
    >>> payment_operation_initialized_started = PaymentOperation(
    ...     payment_method_id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     type=PaymentOperationTypeEnum.initialize,
    ...     status=PaymentOperationStatusEnum.started,
    ... )
    >>> payment_operation_initialized_completed = PaymentOperation(
    ...     payment_method_id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     type=PaymentOperationTypeEnum.initialize,
    ...     status=PaymentOperationStatusEnum.completed,
    ... )
    >>> payment_operation_pay_started = PaymentOperation(
    ...     payment_method_id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     type=PaymentOperationTypeEnum.pay,
    ...     status=PaymentOperationStatusEnum.started,
    ... )
    >>> payment_operation_pay_completed = PaymentOperation(
    ...     payment_method_id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     type=PaymentOperationTypeEnum.pay,
    ...     status=PaymentOperationStatusEnum.completed,
    ... )
    >>> payment_operation_after_pay_started = PaymentOperation(
    ...     payment_method_id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     type=PaymentOperationTypeEnum.after_pay,
    ...     status=PaymentOperationStatusEnum.started,
    ... )
    >>> payment_operation_after_pay_completed = PaymentOperation(
    ...     payment_method_id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     type=PaymentOperationTypeEnum.after_pay,
    ...     status=PaymentOperationStatusEnum.completed,
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
    >>> from django_acquiring.payments.domain import PaymentMethod
    >>> from django_acquiring.payments.domain import PaymentOperation
    >>> payment_operation_initialized_started = PaymentOperation(
    ...     payment_method_id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     type=PaymentOperationTypeEnum.initialize,
    ...     status=PaymentOperationStatusEnum.started,
    ... )
    >>> payment_operation_initialized_completed = PaymentOperation(
    ...     payment_method_id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     type=PaymentOperationTypeEnum.initialize,
    ...     status=PaymentOperationStatusEnum.completed,
    ... )
    >>> payment_operation_pay_started = PaymentOperation(
    ...     payment_method_id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     type=PaymentOperationTypeEnum.pay,
    ...     status=PaymentOperationStatusEnum.started,
    ... )
    >>> payment_operation_pay_completed = PaymentOperation(
    ...     payment_method_id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     type=PaymentOperationTypeEnum.pay,
    ...     status=PaymentOperationStatusEnum.completed,
    ... )
    >>> payment_operation_after_pay_started = PaymentOperation(
    ...     payment_method_id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     type=PaymentOperationTypeEnum.after_pay,
    ...     status=PaymentOperationStatusEnum.started,
    ... )
    >>> payment_operation_after_pay_completed = PaymentOperation(
    ...     payment_method_id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     type=PaymentOperationTypeEnum.after_pay,
    ...     status=PaymentOperationStatusEnum.completed,
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
    >>> from django_acquiring.payments.domain import PaymentMethod
    >>> from django_acquiring.payments.domain import PaymentOperation
    >>> payment_operation_initialized_started = PaymentOperation(
    ...     payment_method_id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     type=PaymentOperationTypeEnum.initialize,
    ...     status=PaymentOperationStatusEnum.started,
    ... )
    >>> payment_operation_initialized_completed = PaymentOperation(
    ...     payment_method_id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     type=PaymentOperationTypeEnum.initialize,
    ...     status=PaymentOperationStatusEnum.completed,
    ... )
    >>> payment_operation_pay_started = PaymentOperation(
    ...     payment_method_id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     type=PaymentOperationTypeEnum.pay,
    ...     status=PaymentOperationStatusEnum.started,
    ... )
    >>> payment_operation_pay_completed = PaymentOperation(
    ...     payment_method_id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     type=PaymentOperationTypeEnum.pay,
    ...     status=PaymentOperationStatusEnum.completed,
    ... )
    >>> payment_operation_after_pay_started = PaymentOperation(
    ...     payment_method_id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     type=PaymentOperationTypeEnum.after_pay,
    ...     status=PaymentOperationStatusEnum.started,
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
        type=PaymentOperationTypeEnum.after_pay,
        status=PaymentOperationStatusEnum.completed,
    ):
        return False

    return True
