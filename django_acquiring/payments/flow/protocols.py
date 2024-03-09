import functools
from dataclasses import dataclass
from typing import Callable

from django_acquiring.payments.protocols import AbstractPaymentMethod, PaymentOperationTypeEnum


@dataclass(kw_only=True, frozen=True)
class SuccessfulOperationResponse:
    success = True
    payment_method: AbstractPaymentMethod
    error_message = None
    payment_operation_type: PaymentOperationTypeEnum


@dataclass(kw_only=True, frozen=True)
class UnsuccessfulOperationResponse:
    success = False
    payment_method = None
    payment_operation_type: PaymentOperationTypeEnum
    error_message: str


@dataclass(kw_only=True, frozen=True)
class OperationResponse:
    success: bool
    payment_method: AbstractPaymentMethod
    payment_operation_type: PaymentOperationTypeEnum
    error_message: str | None = None


# TODO Figure out how to replace this with an OperationResponse typing.Protocol
AbstractOperationResponse = OperationResponse | SuccessfulOperationResponse | UnsuccessfulOperationResponse


def payment_operation_type(function: Callable):
    """This decorator verifies that the name of this function belongs to one of the PaymentOperationTypeEnums"""

    @functools.wraps(function)
    def wrapper(*args, **kwargs):
        if function.__name__ not in PaymentOperationTypeEnum:
            raise TypeError("This function cannot be a payment type")
        return function(*args, **kwargs)

    return wrapper
