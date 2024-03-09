from dataclasses import dataclass
from datetime import datetime
from typing import List
from uuid import UUID

from .protocols import OperationStatusEnum, PaymentOperationTypeEnum


@dataclass
class PaymentOperation:
    type: PaymentOperationTypeEnum
    status: OperationStatusEnum
    payment_method_id: UUID


@dataclass
class PaymentMethod:
    id: UUID
    created_at: datetime
    payment_attempt_id: UUID
    payment_operations: List[PaymentOperation]


@dataclass
class PaymentAttempt:
    id: UUID
    created_at: datetime
    payment_methods: List[PaymentMethod]
