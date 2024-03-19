from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass
class Transaction:
    created_at: datetime
    provider_name: str
    payment_method_id: UUID
    raw_data: dict
