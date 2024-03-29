from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING, Optional
from uuid import UUID

if TYPE_CHECKING:
    from django_acquiring import protocols
    from django_acquiring.enums import OperationStatusEnum, OperationTypeEnum


# TODO frozen=True compatible with protocols.AbstractPaymentOperation (expected settable variable, got read-only attribute)
@dataclass
class PaymentOperation:
    type: "OperationTypeEnum"
    status: "OperationStatusEnum"
    payment_method_id: UUID

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}:{self.type}|{self.status}"


@dataclass
class PaymentMethod:
    id: UUID
    created_at: datetime
    payment_attempt: "protocols.AbstractPaymentAttempt"
    confirmable: bool
    token: Optional["protocols.AbstractToken"] = None
    payment_operations: list["protocols.AbstractPaymentOperation"] = field(default_factory=list, repr=True)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}:{self.id}"

    def has_payment_operation(self, type: "OperationTypeEnum", status: "OperationStatusEnum") -> bool:
        return any(operation.type == type and operation.status == status for operation in self.payment_operations)

    class DoesNotExist(Exception):
        pass


@dataclass
class DraftPaymentMethod:
    payment_attempt: "protocols.AbstractPaymentAttempt"
    confirmable: bool
    token: Optional["protocols.AbstractToken"] = None


@dataclass
class PaymentAttempt:
    id: UUID
    created_at: datetime
    amount: int
    currency: str
    payment_method_ids: list[UUID] = field(default_factory=list)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}:{self.id}|{self.amount}{self.currency}"

    class DoesNotExist(Exception):
        pass


@dataclass
class DraftPaymentAttempt:
    amount: int
    currency: str


@dataclass
class Token:
    created_at: datetime
    token: str
    expires_at: datetime | None = None
    fingerprint: Optional[str] = None
    metadata: dict[str, str | int] | None = None

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}:{self.token}"
