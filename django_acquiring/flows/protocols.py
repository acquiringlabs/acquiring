import functools
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Protocol

from django_acquiring.payments.protocols import AbstractPaymentMethod, PaymentOperationTypeEnum


class AbstractOperationResponse(Protocol):
    success: bool
    actions: List[Dict] = field(default_factory=list)
    payment_operation_type: PaymentOperationTypeEnum
    error_message: str | None = None


def payment_operation_type(function: Callable):
    """This decorator verifies that the name of this function belongs to one of the PaymentOperationTypeEnums"""

    @functools.wraps(function)
    def wrapper(*args, **kwargs):
        if function.__name__ not in PaymentOperationTypeEnum:
            raise TypeError("This function cannot be a payment type")
        return function(*args, **kwargs)

    return wrapper


@dataclass(kw_only=True, frozen=True)
class AbstractBlockResponse:
    success: bool
    payment_method: AbstractPaymentMethod
    actions: List[Dict] = field(default_factory=list)


class AbstractBlock(Protocol):

    def run(self, payment_method: AbstractPaymentMethod) -> AbstractBlockResponse: ...
