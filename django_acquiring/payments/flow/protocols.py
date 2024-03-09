import functools
from dataclasses import dataclass
from typing import Callable, Protocol

from django_acquiring.payments.protocols import AbstractPaymentMethod, PaymentOperationTypeEnum


@dataclass
class OperationResponse(Protocol):
    success: bool
    payment_method: AbstractPaymentMethod | None
    error_message: str | None
    payment_operation_type: PaymentOperationTypeEnum


def payment_operation_type(function: Callable):
    """This decorator verifies that the name of this function belongs to one of the PaymentOperationTypeEnums"""

    @functools.wraps(function)
    def wrapper(*args, **kwargs):
        if function.__name__ not in PaymentOperationTypeEnum:
            raise TypeError("This function cannot be a payment type")
        return function(*args, **kwargs)

    return wrapper
