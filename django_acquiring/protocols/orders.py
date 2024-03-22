from datetime import datetime
from typing import List, Protocol
from uuid import UUID

from django_acquiring.protocols.payments import AbstractPaymentAttempt


class AbstractOrder(Protocol):
    id: UUID
    created_at: datetime
    payment_attempts: List[AbstractPaymentAttempt]

    def __repr__(self) -> str: ...
