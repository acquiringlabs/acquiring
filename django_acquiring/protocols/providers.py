from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Protocol
from uuid import UUID


@dataclass(match_args=False)
class AbstractAdapterResponse(Protocol):
    external_id: Optional[str]  # UUID cannot be imposed across all adapters
    timestamp: Optional[datetime]
    raw_data: dict


@dataclass
class AbstractAdapter(Protocol):
    base_url: str
    provider_name: str


@dataclass
class AbstractTransaction(Protocol):
    external_id: str
    timestamp: datetime
    raw_data: dict
    provider_name: str
    payment_method_id: UUID

    def __repr__(self) -> str: ...
