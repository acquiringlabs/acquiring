from dataclasses import dataclass, field
from datetime import datetime
from typing import List
from uuid import UUID

from .protocols import PaymentOperationStatusEnum, PaymentOperationTypeEnum


# TODO frozen=True compatible with AbstractPaymentOperation (expected settable variable, got read-only attribute)
@dataclass(kw_only=True)
class PaymentOperation:
    type: PaymentOperationTypeEnum
    status: PaymentOperationStatusEnum
    payment_method_id: UUID


@dataclass(kw_only=True)
class PaymentMethod:
    id: UUID
    created_at: datetime
    payment_attempt_id: UUID
    payment_operations: List[PaymentOperation] = field(default_factory=list, repr=True)

    def has_payment_operation(self, type: PaymentOperationTypeEnum, status: PaymentOperationStatusEnum) -> bool:
        return any(operation.type == type and operation.status == status for operation in self.payment_operations)


@dataclass(kw_only=True)
class PaymentAttempt:
    id: UUID
    created_at: datetime
    payment_methods: List[PaymentMethod] = field(default_factory=list, repr=True)
