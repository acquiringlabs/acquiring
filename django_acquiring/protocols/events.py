from typing import Protocol
from uuid import UUID
from django_acquiring.protocols.enums import OperationStatusEnum


class AbstractBlockEvent(Protocol):
    status: OperationStatusEnum
    payment_method_id: UUID
    block_name: str
