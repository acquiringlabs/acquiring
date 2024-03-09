"""
The term protocols is used for types supporting structural subtyping.

Check this link for more info.
https://typing.readthedocs.io/en/latest/spec/protocol.html#protocols
"""

from datetime import datetime
from enum import StrEnum
from typing import Protocol
from uuid import UUID


class AbstractPaymentAttempt(Protocol):
    created_at: datetime
    id: UUID


class PaymentOperationTypeEnum(StrEnum):
    authenticate = "authenticate"
    authorize = "authorize"
    charge = "charge"
    void = "void"
    refund = "refund"
    synchronize = "synchronize"
    mark_as_canceled = "mark_as_canceled"


class OperationStatusEnum(StrEnum):
    started = "started"
    failed = "failed"
    completed = "completed"
    requires_action = "requires_action"
