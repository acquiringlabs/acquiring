import enum
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional


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
    purchase_units: List[PurchaseUnit]


class PayPalStatusEnum(enum.StrEnum):
    CREATED = "CREATED"
    SAVED = "SAVED"
    APPROVED = "APPROVED"
    VOIDED = "VOIDED"
    COMPLETED = "COMPLETED"
    PAYER_ACTION_REQUIRED = "PAYER_ACTION_REQUIRED"
    FAILED = "FAILED"  # Not documented, used for non-2XX responses


@dataclass
class HATEOASLink:
    """
    Hypermedia as the Engine of Application State (HATEOAS) is a constraint of the REST application architecture
    that distinguishes it from other network application architectures.
    """

    """The complete target URL, or link, to combine with the HTTP method to make the related call."""
    href: str

    """
    The link relationship type, or how the href link relates to the previous call.
    See https://www.iana.org/assignments/link-relations/link-relations.xhtml
    """
    rel: str

    """The HTTP method. Use this method to make a request to the target URL."""
    method: Optional[str] = "GET"


@dataclass
class PayPalWebhookData:
    id: str
    event_version: str
    create_time: datetime
    resource_type: str
    resource_version: str
    event_type: str
    summary: str
    raw_data: dict
