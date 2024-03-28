import functools
from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING, Callable, Sequence, Type
from uuid import UUID

if TYPE_CHECKING:
    from django_acquiring import protocols


@dataclass
class Transaction:
    transaction_id: str
    created_at: datetime
    provider_name: str
    payment_method_id: UUID
    raw_data: dict


def wrapped_by_transaction(  # type:ignore[misc]
    function: Callable[..., "protocols.AbstractAdapterResponse"]
) -> Callable:
    """This decorator ensures that a Transaction gets created after interacting with the Provider via its adapter"""
    from django_acquiring import repositories

    repositories.TransactionRepository()

    # TODO Type must be an AbstractAdapter
    @functools.wraps(function)
    def wrapper(self: Type, *args: Sequence, **kwargs: dict) -> "protocols.AbstractAdapterResponse":
        result = function(self, *args, **kwargs)

        return result

    return wrapper
