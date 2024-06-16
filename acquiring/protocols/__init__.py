from typing import Optional, Protocol

from .events import BlockEvent
from .payments import (
    Block,
    BlockResponse,
    DraftItem,
    DraftPaymentAttempt,
    DraftPaymentMethod,
    DraftToken,
    ExistingPaymentAttemptId,
    ExistingPaymentMethodId,
    Item,
    OperationEvent,
    OperationResponse,
    PaymentAttempt,
    PaymentMethod,
    PaymentMilestone,
    Token,
)
from .providers import Adapter, AdapterResponse, Transaction
from .storage import Repository, UnitOfWork


class PaymentMethodSaga(Protocol):
    unit_of_work: "UnitOfWork"

    initialize_block: Optional["Block"]
    process_action_block: Optional["Block"]

    pay_block: "Block"
    after_pay_blocks: list["Block"]

    confirm_block: Optional["Block"]
    after_confirm_blocks: list["Block"]

    def initialize(self, payment_method: "PaymentMethod") -> "OperationResponse": ...

    def process_action(self, payment_method: "PaymentMethod", action_data: dict) -> "OperationResponse": ...

    def __pay(self, payment_method: "PaymentMethod") -> "OperationResponse": ...

    def after_pay(self, payment_method: "PaymentMethod") -> "OperationResponse": ...

    def confirm(self, payment_method: "PaymentMethod") -> "OperationResponse": ...

    def after_confirm(self, payment_method: "PaymentMethod") -> "OperationResponse": ...


__all__ = [
    "Adapter",
    "AdapterResponse",
    "Block",
    "BlockEvent",
    "BlockResponse",
    "DraftItem",
    "DraftPaymentAttempt",
    "DraftPaymentMethod",
    "DraftToken",
    "Item",
    "ExistingPaymentMethodId",
    "ExistingPaymentAttemptId",
    "OperationResponse",
    "PaymentAttempt",
    "PaymentMethodSaga",
    "PaymentMethod",
    "OperationEvent",
    "PaymentMilestone",
    "Repository",
    "Token",
    "Transaction",
    "UnitOfWork",
]
