from django_acquiring.payments.protocols import (
    AbstractPaymentMethod,
    PaymentOperationStatusEnum,
    PaymentOperationTypeEnum,
)


def can_authenticate(payment_method: AbstractPaymentMethod) -> bool:
    """
    Return whether the payment_method can go through the authenticate operation.

    >>> from datetime import datetime
    >>> from django_acquiring.payments.domain import PaymentMethod
    >>> payment_method = PaymentMethod(
    ...     id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     payment_attempt_id="200d03a9-8ac1-489d-894a-54af6de20823",
    ...     created_at=datetime.now(),
    ... )
    >>> can_authenticate(payment_method)
    True

    A Payment Method that has already started cannot go through authenticate.
    >>> from django_acquiring.payments.domain import PaymentOperation
    >>> from django_acquiring.payments.protocols import PaymentOperationTypeEnum, PaymentOperationStatusEnum
    >>> payment_operation_authenticate_started = PaymentOperation(
    ...     payment_method_id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     type=PaymentOperationTypeEnum.authenticate,
    ...     status=PaymentOperationStatusEnum.started,
    ... )
    >>> payment_method = PaymentMethod(
    ...     id="e974291a-f788-47cb-bf15-67104f3845c0",
    ...     payment_attempt_id="200d03a9-8ac1-489d-894a-54af6de20823",
    ...     created_at=datetime.now(),
    ...     payment_operations=[payment_operation_authenticate_started],
    ... )
    >>> can_authenticate(payment_method)
    False
    """
    if payment_method.has_payment_operation(
        type=PaymentOperationTypeEnum.authenticate, status=PaymentOperationStatusEnum.started
    ):
        return False

    return True
