from dataclasses import dataclass, field
from typing import Dict, List

from django_acquiring.protocols.payments import AbstractPaymentMethod


@dataclass
class BlockResponse:
    success: bool
    payment_method: AbstractPaymentMethod
    actions: List[Dict] = field(default_factory=list)
