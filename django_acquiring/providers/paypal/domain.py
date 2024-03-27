import enum
from dataclasses import dataclass


@dataclass
class Amount:
    currency_code: str
    value: str


@dataclass
class PurchaseUnit:
    reference_id: str
    amount: Amount


class OrderIntentEnum(enum.StrEnum):
    CAPTURE = "CAPTURE"
    AUTHORIZE = "AUTHORIZE"


@dataclass
class Order:
    intent: OrderIntentEnum
    purchase_units: list[PurchaseUnit]


class PayPalStatusEnum(enum.StrEnum):
    CREATED = "CREATED"
    SAVED = "SAVED"
    APPROVED = "APPROVED"
    VOIDED = "VOIDED"
    COMPLETED = "COMPLETED"
    PAYER_ACTION_REQUIRED = "PAYER_ACTION_REQUIRED"
    FAILED = "FAILED"  # Not documented, used for non-2XX responses
