from dataclasses import dataclass
from datetime import datetime
from typing import Protocol
from uuid import UUID

from .enums import OperationStatusEnum


@dataclass
class AbstractProviderResponse(Protocol):
    status: OperationStatusEnum
    external_id: UUID


@dataclass
class AbstractProviderInterface(Protocol):
    base_url: str


@dataclass
class AbstractTransaction(Protocol):
    created_at: datetime
    provider_name: str
    payment_method_id: UUID
    raw_data: dict

    def __repr__(self) -> str: ...
