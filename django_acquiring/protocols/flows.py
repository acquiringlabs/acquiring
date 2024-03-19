import functools
from dataclasses import field
from typing import Callable, Dict, List, Protocol, Sequence, runtime_checkable

from django_acquiring.protocols.payments import AbstractPaymentMethod, OperationStatusEnum, OperationTypeEnum


class AbstractOperationResponse(Protocol):
    status: OperationStatusEnum
    actions: List[Dict] = field(default_factory=list)
    payment_operation_type: OperationTypeEnum
    error_message: str | None = None


def payment_operation_type(function: Callable) -> Callable:
    """
    This decorator verifies that the name of this function belongs to one of the OperationTypeEnums

    >>> def initialize(): pass
    >>> payment_operation_type(initialize)()
    >>> def bad_name(): pass
    >>> payment_operation_type(bad_name)()
    Traceback (most recent call last):
        ...
    TypeError: This function cannot be a payment type

    Also, private methods that start with double underscore are allowed.
    This is helpful to make pay a private method.

    >>> def __bad_name(): pass
    >>> payment_operation_type(__bad_name)()
    Traceback (most recent call last):
        ...
    TypeError: This function cannot be a payment type
    >>> def __pay(): pass
    >>> payment_operation_type(__pay)()
    """

    @functools.wraps(function)
    def wrapper(*args, **kwargs):  # type: ignore[no-untyped-def]
        if function.__name__ not in OperationTypeEnum:

            # Private methods that start with double _ and have a name that belongs to enum are also allowed
            if function.__name__.startswith("__") and function.__name__[2:] in OperationTypeEnum:
                return function(*args, **kwargs)

            raise TypeError("This function cannot be a payment type")

        return function(*args, **kwargs)

    return wrapper


class AbstractBlockResponse(Protocol):
    status: OperationStatusEnum
    payment_method: AbstractPaymentMethod
    actions: List[Dict] = field(default_factory=list)
    error_message: str | None = None


@runtime_checkable
class AbstractBlock(Protocol):

    def run(self, payment_method: AbstractPaymentMethod, *args: Sequence, **kwargs: Dict) -> AbstractBlockResponse: ...
