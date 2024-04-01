from dataclasses import dataclass
from datetime import datetime
from typing import Any, Optional, Protocol
from uuid import UUID
from django_acquiring.protocols import repositories


@dataclass(match_args=False)
class AbstractAdapterResponse(Protocol):  # type:ignore[misc]
    external_id: Optional[str]  # UUID cannot be imposed across all adapters
    timestamp: Optional[datetime]
    raw_data: dict

    # TODO implement status as StrEnum and all the classes that inherit from StrEnum. TypeVar? bound?
    status: Any  # type:ignore[misc]


@dataclass
class AbstractAdapter(Protocol):
    base_url: str
    provider_name: str
    transaction_repository: repositories.AbstractRepository


@dataclass
class AbstractTransaction(Protocol):
    external_id: str
    timestamp: datetime
    raw_data: dict
    provider_name: str
    payment_method_id: UUID

    def __repr__(self) -> str: ...
