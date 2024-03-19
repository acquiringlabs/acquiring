from dataclasses import dataclass
from uuid import UUID

from django_acquiring.protocols.payments import OperationStatusEnum


@dataclass
class BlockEvent:
    status: OperationStatusEnum
    payment_method_id: UUID
    block_name: str

    class DoesNotExist(Exception):
        pass
