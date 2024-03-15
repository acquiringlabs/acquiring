from dataclasses import dataclass
from uuid import UUID
from django_acquiring.protocols.payments import PaymentOperationStatusEnum


@dataclass
class BlockEvent:
    status: PaymentOperationStatusEnum
    payment_method_id: UUID
    block_name: str
