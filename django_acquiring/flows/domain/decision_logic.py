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

    A Payment Method that has already started cannot go through initialize.
    >>> from django_acquiring.payments.domain import PaymentOperation
    >>> from django_acquiring.protocols.payments import PaymentOperationTypeEnum, PaymentOperationStatusEnum
    >>> payment_operation_initialize_started = PaymentOperation(
    ...     payment_method_id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     type=PaymentOperationTypeEnum.initialize,
    ...     status=PaymentOperationStatusEnum.started,
    ... )
    >>> payment_method = PaymentMethod(
    ...     id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     payment_attempt_id="200d03a9-8ac1-489d-894a-54af6de20823",
    ...     created_at=datetime.now(),
    ...     payment_operations=[payment_operation_initialize_started],
    ... )
    >>> can_initialize(payment_method)
    False
    """
    if payment_method.has_payment_operation(
        type=PaymentOperationTypeEnum.initialize, status=PaymentOperationStatusEnum.started
    ):
        return False

    return True
