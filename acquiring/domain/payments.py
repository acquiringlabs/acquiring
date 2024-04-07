from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING, Optional, Sequence
from uuid import UUID

if TYPE_CHECKING:
    from acquiring import enums, protocols


# TODO frozen=True compatible with protocols.AbstractPaymentOperation (expected settable variable, got read-only attribute)
@dataclass
class PaymentOperation:
    type: "enums.OperationTypeEnum"
    status: "enums.OperationStatusEnum"
    payment_method_id: UUID

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}:{self.type}|{self.status}"

    class DuplicateError(Exception):
        pass


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

    def has_payment_operation(self, type: "enums.OperationTypeEnum", status: "enums.OperationStatusEnum") -> bool:
        return any(operation.type == type and operation.status == status for operation in self.payment_operations)

    class DoesNotExist(Exception):
        pass


@dataclass
class DraftPaymentMethod:
    payment_attempt: "protocols.AbstractPaymentAttempt"
    confirmable: bool
    token: Optional["protocols.AbstractToken"] = None


@dataclass
class Item:
    id: UUID
    created_at: datetime
    payment_attempt_id: UUID
    reference: str
    name: str
    quantity: int
    quantity_unit: Optional[str]
    unit_price: int

    class InvalidTotalAmount(Exception):
        pass


@dataclass
class DraftItem:
    reference: str
    name: str
    quantity: int
    unit_price: int
    quantity_unit: Optional[str] = None


@dataclass
class PaymentAttempt:
    id: UUID
    created_at: datetime
    amount: int
    currency: str
    payment_method_ids: list[UUID] = field(default_factory=list)
    items: Sequence["protocols.AbstractItem"] = field(default_factory=list)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}:{self.id}|{self.amount}{self.currency}"

    class DoesNotExist(Exception):
        pass


@dataclass
class DraftPaymentAttempt:
    amount: int
    currency: str
    items: Sequence["protocols.AbstractDraftItem"] = field(default_factory=list)


@dataclass
class Token:
    created_at: datetime
    token: str
    metadata: Optional[dict[str, str | int]] = field(default_factory=dict)
    expires_at: Optional[datetime] = None
    fingerprint: Optional[str] = None

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}:{self.token}"
