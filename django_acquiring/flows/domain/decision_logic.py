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
    return True
