from dataclasses import dataclass, field
from datetime import datetime
from typing import List
from uuid import UUID

from django_acquiring.protocols.payments import (
    AbstractPaymentMethod,
    AbstractPaymentOperation,
    PaymentOperationStatusEnum,
    PaymentOperationTypeEnum,
)


# TODO frozen=True compatible with AbstractPaymentOperation (expected settable variable, got read-only attribute)
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
    payment_operations: List[AbstractPaymentOperation] = field(default_factory=list, repr=True)

    def has_payment_operation(self, type: PaymentOperationTypeEnum, status: PaymentOperationStatusEnum) -> bool:
        return any(operation.type == type and operation.status == status for operation in self.payment_operations)

    class DoesNotExist(Exception):
        pass


@dataclass
class PaymentAttempt:
    id: UUID
    created_at: datetime
    payment_methods: List[AbstractPaymentMethod] = field(default_factory=list, repr=True)

    class DoesNotExist(Exception):
        pass
