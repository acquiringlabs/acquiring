"""
The term protocols is used for types supporting structural subtyping.

Check this link for more info.
https://typing.readthedocs.io/en/latest/spec/protocol.html#protocols
"""

from datetime import datetime
from typing import List, Protocol
from uuid import UUID

from .enums import OperationStatusEnum, OperationTypeEnum


class AbstractPaymentOperation(Protocol):
    payment_method_id: UUID
    type: OperationTypeEnum
    status: OperationStatusEnum

    def __repr__(self) -> str: ...


# TODO Have this class the DoesNotExist internal class
class AbstractPaymentMethod(Protocol):
    id: UUID
    created_at: datetime
    payment_attempt_id: UUID
    confirmable: bool
    payment_operations: List[AbstractPaymentOperation]

    def __repr__(self) -> str: ...

    def has_payment_operation(
        self: "AbstractPaymentMethod",
        type: OperationTypeEnum,
        status: OperationStatusEnum,
    ) -> bool: ...


class AbstractDraftPaymentMethod(Protocol):
    id: None
    created_at: None
    payment_attempt_id: UUID
    confirmable: bool


# TODO Have this class the DoesNotExist internal class
class AbstractPaymentAttempt(Protocol):
    id: UUID
    order_id: UUID
    created_at: datetime
    amount: int
    currency: str

    def __repr__(self) -> str: ...


class AbstractDraftPaymentAttempt(Protocol):
    id: None
    order_id: UUID
    created_at: None
    amount: int
    currency: str
