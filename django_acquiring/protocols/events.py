from typing import Protocol
from uuid import UUID


class AbstractBlockEvent(Protocol):
    success: bool
    payment_method_id: UUID
    block_name: str
