from typing import Protocol, Callable
from dataclasses import dataclass
from django_acquiring.payments.protocols import AbstractPaymentAttempt, StageNameEnum
import functools


@dataclass
class StageResponse(Protocol):
    success: bool
    payment_attempt: AbstractPaymentAttempt | None
    error_message: str | None
    stage_name: StageNameEnum


def payment_type(function: Callable):
    """This decorator verifies that the name of this function belongs to one of the StageNameEnums"""

    @functools.wraps(function)
    def wrapper(*args, **kwargs):
        if function.__name__ not in StageNameEnum:
            raise TypeError("This function cannot be a payment type")
        return function(*args, **kwargs)

    return wrapper
