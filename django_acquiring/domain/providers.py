import functools
from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING, Callable, Sequence
from uuid import UUID
from django_acquiring import domain

if TYPE_CHECKING:
    from django_acquiring import protocols


@dataclass
class Transaction:
    external_id: str
    created_at: datetime
    provider_name: str
    payment_method_id: UUID
    raw_data: dict


def wrapped_by_transaction(  # type:ignore[misc]
    function: Callable[..., "protocols.AbstractAdapterResponse"]
) -> Callable:
    """This decorator ensures that a Transaction gets created after interacting with the Provider via its adapter"""
    from django_acquiring import repositories

    repository = repositories.TransactionRepository()

    @functools.wraps(function)
    def wrapper(
        self: "protocols.AbstractAdapter",
        payment_method: "protocols.AbstractPaymentMethod",
        *args: Sequence,
        **kwargs: dict,
    ) -> "protocols.AbstractAdapterResponse":
        result = function(self, payment_method, *args, **kwargs)

        if result.success is True and result.external_id is not None:
            transaction = domain.Transaction(
                external_id=result.external_id,
                created_at=result.timestamp,
                provider_name=self.provider_name,
                payment_method_id=payment_method.id,
                raw_data=result.raw_data,
            )
            repository.add(transaction)

        return result

    return wrapper
