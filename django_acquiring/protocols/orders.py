from datetime import datetime
from typing import Protocol
from uuid import UUID

from django_acquiring.protocols.payments import AbstractPaymentAttempt


class AbstractOrder(Protocol):
    id: UUID
    created_at: datetime
    payment_attempts: list[AbstractPaymentAttempt]

    def __repr__(self) -> str: ...
