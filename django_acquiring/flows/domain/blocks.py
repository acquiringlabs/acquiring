from dataclasses import dataclass, field
from typing import Dict, List

from django_acquiring.protocols.payments import AbstractPaymentMethod, PaymentOperationStatusEnum


@dataclass
class BlockResponse:
    status: PaymentOperationStatusEnum
    payment_method: AbstractPaymentMethod
    actions: List[Dict] = field(default_factory=list)
    error_message: str | None = None
