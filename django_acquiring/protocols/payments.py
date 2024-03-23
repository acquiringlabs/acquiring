"""
The term protocols is used for types supporting structural subtyping.

Check this link for more info.
https://typing.readthedocs.io/en/latest/spec/protocol.html#protocols
"""

from dataclasses import field
from datetime import datetime
from typing import Optional, Protocol, Sequence, runtime_checkable
from uuid import UUID

from django_acquiring.enums import OperationStatusEnum, OperationTypeEnum


class AbstractPaymentOperation(Protocol):
    payment_method_id: UUID
    type: OperationTypeEnum
    status: OperationStatusEnum

    def __repr__(self) -> str: ...


class AbstractToken(Protocol):
    created_at: datetime
    expires_at: datetime | None
    token: str
    fingerprint: Optional[str]
    metadata: dict[str, str | int] | None

    def __repr__(self) -> str: ...


# TODO Have this class the DoesNotExist internal class
class AbstractPaymentMethod(Protocol):
    id: UUID
    created_at: datetime
    token: AbstractToken | None
    payment_attempt_id: UUID
    confirmable: bool
    payment_operations: list[AbstractPaymentOperation]

    def __repr__(self) -> str: ...

    def has_payment_operation(
        self: "AbstractPaymentMethod",
        type: OperationTypeEnum,
        status: OperationStatusEnum,
    ) -> bool: ...


class AbstractDraftPaymentMethod(Protocol):
    payment_attempt_id: UUID
    confirmable: bool
    token: AbstractToken | None = None


# TODO Have this class the DoesNotExist internal class
class AbstractPaymentAttempt(Protocol):
    id: UUID
    order_id: UUID
    created_at: datetime
    amount: int
    currency: str

    def __repr__(self) -> str: ...


class AbstractDraftPaymentAttempt(Protocol):
    order_id: UUID
    amount: int
    currency: str


class AbstractOrder(Protocol):
    id: UUID
    created_at: datetime
    payment_attempts: list[AbstractPaymentAttempt]

    def __repr__(self) -> str: ...


class AbstractOperationResponse(Protocol):
    status: OperationStatusEnum
    actions: list[dict] = field(default_factory=list)
    type: OperationTypeEnum
    error_message: Optional[str] = None


class AbstractBlockResponse(Protocol):
    status: OperationStatusEnum
    actions: list[dict] = field(default_factory=list)
    error_message: Optional[str] = None


@runtime_checkable
class AbstractBlock(Protocol):

    def __init__(self, *args, **kwargs) -> None: ...  # type:ignore[no-untyped-def]

    def run(self, payment_method: AbstractPaymentMethod, *args: Sequence, **kwargs: dict) -> AbstractBlockResponse: ...
