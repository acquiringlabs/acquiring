import functools
from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING, Callable, Sequence
from uuid import UUID
from acquiring import domain

if TYPE_CHECKING:
    from acquiring import protocols


@dataclass
class Transaction:
    external_id: str
    timestamp: datetime
    raw_data: dict
    provider_name: str
    payment_method_id: UUID

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}:{self.provider_name}|{self.external_id}"


def wrapped_by_transaction(  # type:ignore[misc]
    function: Callable[..., "protocols.AbstractAdapterResponse"]
) -> Callable[..., "protocols.AbstractAdapterResponse"]:
    """This decorator ensures that a Transaction gets created after interacting with the Provider via its adapter"""

    @functools.wraps(function)
    def wrapper(
        self: "protocols.AbstractAdapter",
        payment_method: "protocols.AbstractPaymentMethod",
        *args: Sequence,
        **kwargs: dict,
    ) -> "protocols.AbstractAdapterResponse":
        result = function(self, payment_method, *args, **kwargs)

        # A transaction is created only when the Adapter Response is successful
        if result.timestamp is not None and result.external_id is not None:
            transaction = domain.Transaction(
                external_id=result.external_id,
                timestamp=result.timestamp,
                raw_data=result.raw_data,
                provider_name=self.provider_name,
                payment_method_id=payment_method.id,
            )
            self.transaction_repository.add(transaction)

        return result

    return wrapper
