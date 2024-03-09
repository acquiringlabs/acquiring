from dataclasses import dataclass, field
from typing import Dict, List, Protocol

from django_acquiring.payments.protocols import AbstractPaymentMethod


@dataclass(kw_only=True, frozen=True)
class AbstractBlockResponse:
    success: bool
    payment_method: AbstractPaymentMethod
    actions: List[Dict] = field(default_factory=list)


class AbstractBlock(Protocol):

    def run(self, payment_method: AbstractPaymentMethod) -> AbstractBlockResponse: ...
