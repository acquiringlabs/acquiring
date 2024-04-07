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

from .repositories import AbstractRepository


class AbstractPaymentOperation(Protocol):
    payment_method_id: UUID
    type: OperationTypeEnum
    status: OperationStatusEnum

    def __repr__(self) -> str: ...


class AbstractToken(Protocol):
    created_at: datetime
    token: str
    metadata: Optional[dict[str, str | int]]
    expires_at: Optional[datetime]
    fingerprint: Optional[str]

    def __repr__(self) -> str: ...


class AbstractDraftItem(Protocol):
    reference: str
    name: str
    quantity: int
    unit_price: int
    quantity_unit: Optional[str]


class AbstractItem(Protocol):
    id: UUID
    created_at: datetime
    payment_attempt_id: UUID
    reference: str
    name: str
    quantity: int
    quantity_unit: Optional[str]
    unit_price: int


# TODO Have this class the DoesNotExist internal class
class AbstractPaymentAttempt(Protocol):
    id: UUID
    created_at: datetime
    amount: int
    currency: str
    payment_method_ids: list[UUID]
    items: Sequence[AbstractItem] = field(default_factory=list)

    def __repr__(self) -> str: ...


# TODO Have this class the DoesNotExist internal class
class AbstractPaymentMethod(Protocol):
    id: UUID
    created_at: datetime
    token: AbstractToken | None
    payment_attempt: AbstractPaymentAttempt
    confirmable: bool
    payment_operations: list[AbstractPaymentOperation]

    def __repr__(self) -> str: ...

    def has_payment_operation(
        self: "AbstractPaymentMethod",
        type: OperationTypeEnum,
        status: OperationStatusEnum,
    ) -> bool: ...


class AbstractDraftPaymentMethod(Protocol):
    payment_attempt: AbstractPaymentAttempt
    confirmable: bool
    token: AbstractToken | None = None


class AbstractDraftPaymentAttempt(Protocol):
    amount: int
    currency: str
    items: Sequence[AbstractDraftItem] = field(default_factory=list)


class AbstractOperationResponse(Protocol):
    status: OperationStatusEnum
    payment_method: Optional["AbstractPaymentMethod"]
    type: OperationTypeEnum
    error_message: Optional[str]
    actions: list[dict]


class AbstractBlockResponse(Protocol):
    status: OperationStatusEnum
    actions: list[dict] = field(default_factory=list)
    error_message: Optional[str] = None


@runtime_checkable
class AbstractBlock(Protocol):
    block_event_repository: AbstractRepository

    def run(self, payment_method: AbstractPaymentMethod, *args: Sequence, **kwargs: dict) -> AbstractBlockResponse: ...
