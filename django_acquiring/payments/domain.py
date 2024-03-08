from dataclasses import dataclass
from datetime import datetime
from typing import List
from uuid import UUID

from .protocols import StageNameEnum, StageStatusEnum


@dataclass
class StageEvent:
    name: StageNameEnum
    status: StageStatusEnum
    payment_method_id: UUID


@dataclass
class PaymentMethod:
    id: UUID
    created_at: datetime
    payment_attempt_id: UUID
    stage_events: List[StageEvent]


@dataclass
class PaymentAttempt:
    id: UUID
    created_at: datetime
    payment_methods: List[PaymentMethod]
