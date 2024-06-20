"""
The term protocols is used for types supporting structural subtyping.

Check this link for more info.
https://typing.readthedocs.io/en/latest/spec/protocol.html#protocols
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import NewType, Optional, Protocol, Sequence, runtime_checkable
from uuid import UUID

from acquiring import enums

from .storage import UnitOfWork

ExistingPaymentMethodId = NewType("ExistingPaymentMethodId", UUID)
ExistingPaymentAttemptId = NewType("ExistingPaymentAttemptId", UUID)


@dataclass(frozen=True, match_args=False)
class OperationEvent(Protocol):
    created_at: datetime
    payment_method_id: ExistingPaymentMethodId
    type: enums.OperationTypeEnum
    status: enums.OperationStatusEnum

    def __repr__(self) -> str: ...


@dataclass(frozen=True, match_args=False)
class Milestone(Protocol):
    created_at: datetime
    payment_method_id: ExistingPaymentMethodId
    payment_attempt_id: ExistingPaymentAttemptId
    type: enums.MilestoneTypeEnum


class DraftToken(Protocol):
    timestamp: datetime
    token: str
    metadata: Optional[dict[str, str | int]]
    expires_at: Optional[datetime]
    fingerprint: Optional[str]


class Token(Protocol):
    timestamp: datetime
    token: str
    payment_method_id: ExistingPaymentMethodId
    metadata: Optional[dict[str, str | int]]
    expires_at: Optional[datetime]
    fingerprint: Optional[str]

    def __repr__(self) -> str: ...


class DraftItem(Protocol):
    reference: str
    name: str
    quantity: int
    unit_price: int
    quantity_unit: Optional[str]


class Item(Protocol):
    id: UUID
    created_at: datetime
    payment_attempt_id: ExistingPaymentAttemptId
    reference: str
    name: str
    quantity: int
    quantity_unit: Optional[str]
    unit_price: int


# TODO Have this class the DoesNotExist internal class
class PaymentAttempt(Protocol):
    id: ExistingPaymentAttemptId
    created_at: datetime
    amount: int
    currency: str
    payment_methods: list["PaymentMethod"]
    items: Sequence[Item] = field(default_factory=list)

    def __repr__(self) -> str: ...


# TODO Have this class the DoesNotExist internal class
class PaymentMethod(Protocol):
    id: ExistingPaymentMethodId
    created_at: datetime
    tokens: list[Token]
    payment_attempt_id: ExistingPaymentAttemptId
    operation_events: list[OperationEvent]

    def __repr__(self) -> str: ...

    def has_operation_event(
        self: "PaymentMethod",
        type: enums.OperationTypeEnum,
        status: enums.OperationStatusEnum,
    ) -> bool: ...

    def count_operation_event(
        self: "PaymentMethod",
        type: enums.OperationTypeEnum,
        status: enums.OperationStatusEnum,
    ) -> int: ...


class DraftPaymentMethod(Protocol):
    payment_attempt_id: ExistingPaymentAttemptId
    tokens: list[DraftToken]


class DraftPaymentAttempt(Protocol):
    amount: int
    currency: str
    items: Sequence[DraftItem] = field(default_factory=list)


class OperationResponse(Protocol):
    status: enums.OperationStatusEnum
    payment_method: Optional["PaymentMethod"]
    type: enums.OperationTypeEnum
    error_message: Optional[str]
    actions: list[dict]


class BlockResponse(Protocol):
    status: enums.OperationStatusEnum
    actions: list[dict] = field(default_factory=list)
    error_message: Optional[str] = None


@runtime_checkable
class Block(Protocol):

    def run(
        self, unit_of_work: UnitOfWork, payment_method: PaymentMethod, *args: Sequence, **kwargs: dict
    ) -> BlockResponse: ...
