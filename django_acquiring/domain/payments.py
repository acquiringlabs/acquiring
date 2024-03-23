from dataclasses import dataclass, field
from datetime import datetime
from typing import List
from uuid import UUID

from django_acquiring.protocols.enums import OperationStatusEnum, OperationTypeEnum
from django_acquiring.protocols.payments import AbstractPaymentMethod, AbstractPaymentOperation, AbstractToken


# TODO frozen=True compatible with AbstractPaymentOperation (expected settable variable, got read-only attribute)
@dataclass
class PaymentOperation:
    type: OperationTypeEnum
    status: OperationStatusEnum
    payment_method_id: UUID

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}:{self.type}|{self.status}"


@dataclass
class PaymentMethod:
    id: UUID
    created_at: datetime
    payment_attempt_id: UUID
    confirmable: bool
    token: AbstractToken | None = None
    payment_operations: List[AbstractPaymentOperation] = field(default_factory=list, repr=True)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}:{self.id}"

    def has_payment_operation(self, type: OperationTypeEnum, status: OperationStatusEnum) -> bool:
        return any(operation.type == type and operation.status == status for operation in self.payment_operations)

    class DoesNotExist(Exception):
        pass


@dataclass
class DraftPaymentMethod:
    payment_attempt_id: UUID
    confirmable: bool
    token: AbstractToken | None = None


@dataclass
class PaymentAttempt:
    id: UUID
    order_id: UUID
    created_at: datetime
    amount: int
    currency: str
    payment_methods: List[AbstractPaymentMethod] = field(default_factory=list)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}:{self.id}|{self.amount}{self.currency}"

    class DoesNotExist(Exception):
        pass


@dataclass
class DraftPaymentAttempt:
    order_id: UUID
    amount: int
    currency: str


@dataclass
class Token:
    created_at: datetime
    token: str
    expires_at: datetime | None = None
    fingerprint: str | None = None
    metadata: dict[str, str | int] | None = None

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}:{self.token}"
