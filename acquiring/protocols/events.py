from dataclasses import dataclass
from typing import Protocol
from uuid import UUID

from acquiring.enums import OperationStatusEnum


@dataclass(frozen=True, match_args=False)
class BlockEvent(Protocol):
    status: OperationStatusEnum
    payment_method_id: UUID
    block_name: str

    def __repr__(self) -> str: ...
