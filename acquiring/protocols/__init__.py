from typing import Optional, Protocol

from .events import AbstractBlockEvent
from .payments import (
    AbstractBlock,
    AbstractBlockResponse,
    AbstractDraftItem,
    AbstractDraftPaymentAttempt,
    AbstractDraftPaymentMethod,
    AbstractItem,
    AbstractOperationResponse,
    AbstractPaymentAttempt,
    AbstractPaymentMethod,
    AbstractPaymentOperation,
    AbstractToken,
)
from .providers import AbstractAdapter, AbstractAdapterResponse, AbstractTransaction
from .repositories import AbstractRepository


class AbstractPaymentFlow(Protocol):
    payment_method_repository: "AbstractRepository"
    payment_operation_repository: "AbstractRepository"

    initialize_block: Optional["AbstractBlock"]
    process_action_block: Optional["AbstractBlock"]

    pay_blocks: list["AbstractBlock"]
    after_pay_blocks: list["AbstractBlock"]

    confirm_block: Optional["AbstractBlock"]
    after_confirm_blocks: list["AbstractBlock"]

    def initialize(self, payment_method: "AbstractPaymentMethod") -> "AbstractOperationResponse": ...

    def process_action(
        self, payment_method: "AbstractPaymentMethod", action_data: dict
    ) -> "AbstractOperationResponse": ...

    def __pay(self, payment_method: "AbstractPaymentMethod") -> "AbstractOperationResponse": ...

    def after_pay(self, payment_method: "AbstractPaymentMethod") -> "AbstractOperationResponse": ...

    def confirm(self, payment_method: "AbstractPaymentMethod") -> "AbstractOperationResponse": ...

    def after_confirm(self, payment_method: "AbstractPaymentMethod") -> "AbstractOperationResponse": ...


__all__ = [
    "AbstractAdapter",
    "AbstractAdapterResponse",
    "AbstractBlock",
    "AbstractBlockEvent",
    "AbstractBlockResponse",
    "AbstractDraftItem",
    "AbstractDraftPaymentAttempt",
    "AbstractDraftPaymentMethod",
    "AbstractItem",
    "AbstractOperationResponse",
    "AbstractPaymentAttempt",
    "AbstractPaymentFlow",
    "AbstractPaymentMethod",
    "AbstractPaymentOperation",
    "AbstractRepository",
    "AbstractToken",
    "AbstractTransaction",
]

assert __all__ == sorted(__all__), sorted(__all__)
assert all(protocol.startswith("Abstract") for protocol in __all__)
