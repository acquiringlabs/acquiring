from typing import Protocol
from uuid import UUID
from django_acquiring.protocols.payments import PaymentOperationStatusEnum


class AbstractBlockEvent(Protocol):
    status: PaymentOperationStatusEnum
    payment_method_id: UUID
    block_name: str
