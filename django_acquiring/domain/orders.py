from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

if TYPE_CHECKING:
    from django_acquiring.protocols.payments import AbstractPaymentAttempt


@dataclass
class Order:
    id: UUID
    created_at: datetime
    payment_attempts: list["AbstractPaymentAttempt"]

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}:{self.id}"
