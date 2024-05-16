"""
The term protocols is used for types supporting structural subtyping.

Check this link for more info.
https://typing.readthedocs.io/en/latest/spec/protocol.html#protocols
"""

from dataclasses import field
from datetime import datetime
from typing import Optional, Protocol, Sequence, runtime_checkable
from uuid import UUID

from acquiring.enums import OperationStatusEnum, OperationTypeEnum

from .storage import UnitOfWork


class PaymentOperation(Protocol):
    payment_method_id: UUID
    type: OperationTypeEnum
    status: OperationStatusEnum

    def __repr__(self) -> str: ...


class DraftToken(Protocol):
    created_at: datetime
    token: str
    metadata: Optional[dict[str, str | int]]
    expires_at: Optional[datetime]
    fingerprint: Optional[str]


class Token(Protocol):
    created_at: datetime
    token: str
    payment_method_id: UUID
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
    payment_attempt_id: UUID
    reference: str
    name: str
    quantity: int
    quantity_unit: Optional[str]
    unit_price: int


# TODO Have this class the DoesNotExist internal class
class PaymentAttempt(Protocol):
    id: UUID
    created_at: datetime
    amount: int
    currency: str
    payment_method_ids: list[UUID]
    items: Sequence[Item] = field(default_factory=list)

    def __repr__(self) -> str: ...


# TODO Have this class the DoesNotExist internal class
class PaymentMethod(Protocol):
    id: UUID
    created_at: datetime
    tokens: list[Token]
    payment_attempt: PaymentAttempt
    confirmable: bool
    payment_operations: list[PaymentOperation]

    def __repr__(self) -> str: ...

    def has_payment_operation(
        self: "PaymentMethod",
        type: OperationTypeEnum,
        status: OperationStatusEnum,
    ) -> bool: ...


class DraftPaymentMethod(Protocol):
    payment_attempt: PaymentAttempt
    confirmable: bool
    tokens: list[DraftToken]


class DraftPaymentAttempt(Protocol):
    amount: int
    currency: str
    items: Sequence[DraftItem] = field(default_factory=list)


class OperationResponse(Protocol):
    status: OperationStatusEnum
    payment_method: Optional["PaymentMethod"]
    type: OperationTypeEnum
    error_message: Optional[str]
    actions: list[dict]


class BlockResponse(Protocol):
    status: OperationStatusEnum
    actions: list[dict] = field(default_factory=list)
    error_message: Optional[str] = None


@runtime_checkable
class Block(Protocol):

    def run(
        self, unit_of_work: UnitOfWork, payment_method: PaymentMethod, *args: Sequence, **kwargs: dict
    ) -> BlockResponse: ...
