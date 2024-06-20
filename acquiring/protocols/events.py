from dataclasses import dataclass
from datetime import datetime
from typing import Protocol
from acquiring import enums
from . import primitives


@dataclass(frozen=True, match_args=False)
class BlockEvent(Protocol):
    created_at: datetime
    status: enums.OperationStatusEnum
    payment_method_id: primitives.ExistingPaymentMethodId
    block_name: str

    def __repr__(self) -> str: ...
