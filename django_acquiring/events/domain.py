from dataclasses import dataclass
from uuid import UUID


@dataclass
class BlockEvent:
    success: bool
    payment_method_id: UUID
    block_name: str
