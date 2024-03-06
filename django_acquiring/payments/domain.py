from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass
class PaymentAttempt:
    id: UUID
    created_at: datetime
