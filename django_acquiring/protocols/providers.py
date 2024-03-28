from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Protocol, runtime_checkable
from uuid import UUID


@runtime_checkable
@dataclass(match_args=False)
class AbstractAdapterResponse(Protocol):
    success: bool
    timestamp: datetime
    external_id: Optional[str]  # UUID cannot be imposed across all adapters
    raw_data: dict


@dataclass
class AbstractAdapter(Protocol):
    base_url: str
    provider_name: str


@dataclass
class AbstractTransaction(Protocol):
    external_id: str
    created_at: datetime
    provider_name: str
    payment_method_id: UUID
    raw_data: dict

    def __repr__(self) -> str: ...
