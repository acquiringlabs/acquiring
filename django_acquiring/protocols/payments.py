"""
The term protocols is used for types supporting structural subtyping.

Check this link for more info.
https://typing.readthedocs.io/en/latest/spec/protocol.html#protocols
"""

from datetime import datetime
from enum import StrEnum
from typing import Protocol
from uuid import UUID


class PaymentOperationTypeEnum(StrEnum):
    initialize = "initialize"
    authorize = "authorize"
    charge = "charge"
    void = "void"
    refund = "refund"
    synchronize = "synchronize"
    mark_as_canceled = "mark_as_canceled"


class PaymentOperationStatusEnum(StrEnum):
    started = "started"
    failed = "failed"
    completed = "completed"
    requires_action = "requires_action"


class AbstractPaymentOperation(Protocol):
    payment_method_id: UUID
    type: PaymentOperationTypeEnum
    status: PaymentOperationStatusEnum


class AbstractPaymentMethod(Protocol):
    id: UUID
    created_at: datetime
    payment_attempt_id: UUID
    payment_operations: list

    def has_payment_operation(
        self: "AbstractPaymentMethod",
        type: PaymentOperationTypeEnum,
        status: PaymentOperationStatusEnum,
    ): ...


class AbstractPaymentAttempt(Protocol):
    id: UUID
    created_at: datetime