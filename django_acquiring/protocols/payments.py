"""
The term protocols is used for types supporting structural subtyping.

Check this link for more info.
https://typing.readthedocs.io/en/latest/spec/protocol.html#protocols
"""

from datetime import datetime
from typing import Optional, Protocol
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
