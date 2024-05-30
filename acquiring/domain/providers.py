import functools
from dataclasses import dataclass
from datetime import datetime
from typing import Callable, Sequence
from uuid import UUID

from acquiring import domain, protocols


@dataclass(frozen=True)
class Transaction:
    external_id: str
    timestamp: datetime
    raw_data: str
    provider_name: str
    payment_method_id: UUID

    def __repr__(self) -> str:
        """String representation of the class"""
        return f"{self.__class__.__name__}:{self.provider_name}|{self.external_id}"


def wrapped_by_transaction(  # type:ignore[misc]
    function: Callable[..., "protocols.AdapterResponse"]
) -> Callable[..., "protocols.AdapterResponse"]:
    """This decorator ensures that a Transaction gets created after interacting with the Provider via its adapter"""

    @functools.wraps(function)
    def wrapper(
        self: "protocols.Adapter",
        unit_of_work: "protocols.UnitOfWork",
        payment_method: "protocols.PaymentMethod",
        *args: Sequence,
        **kwargs: dict,
    ) -> "protocols.AdapterResponse":
        result = function(self, unit_of_work, payment_method, *args, **kwargs)

        # A transaction is created only when the Adapter Response is successful
        if result.timestamp is not None and result.external_id is not None:
            transaction = domain.Transaction(
                external_id=result.external_id,
                timestamp=result.timestamp,
                raw_data=result.raw_data,
                provider_name=self.provider_name,
                payment_method_id=payment_method.id,
            )
            with unit_of_work as uow:
                uow.transactions.add(transaction)
                uow.commit()

        return result

    return wrapper
