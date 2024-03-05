from uuid import UUID
from datetime import datetime
from dataclasses import dataclass


@dataclass
class PaymentAttempt:
    id: UUID
    created_at: datetime
