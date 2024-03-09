from dataclasses import dataclass, field
from datetime import datetime
from typing import List
from uuid import UUID

from .protocols import PaymentOperationStatusEnum, PaymentOperationTypeEnum


@dataclass
class PaymentOperation:
    type: PaymentOperationTypeEnum
    status: PaymentOperationStatusEnum
    payment_method_id: UUID


@dataclass
class PaymentMethod:
    id: UUID
    created_at: datetime
    payment_attempt_id: UUID
    payment_operations: List[PaymentOperation] = field(default_factory=list)

    def has_payment_operation(self, type: PaymentOperationTypeEnum, status: PaymentOperationStatusEnum) -> bool:
        for operation in self.payment_operations:
            if operation.type == type and operation.status == status:
                return True
        return False


@dataclass
class PaymentAttempt:
    id: UUID
    created_at: datetime
    payment_methods: List[PaymentMethod] = field(default_factory=list)
