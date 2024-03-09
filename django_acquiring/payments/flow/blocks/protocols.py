from dataclasses import dataclass
from typing import Protocol

from django_acquiring.payments.protocols import AbstractPaymentMethod


@dataclass(kw_only=True, frozen=True)
class AbstractBlockResponse:
    success: bool
    payment_method: AbstractPaymentMethod


class AbstractBlock(Protocol):

    def run(self, payment_method: AbstractPaymentMethod) -> AbstractBlockResponse: ...
