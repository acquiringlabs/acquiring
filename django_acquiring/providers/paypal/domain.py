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


class ShippingPreferenceEnum(enum.StrEnum):
    """https://developer.paypal.com/docs/api/orders/v2/#orders_create!path=payment_source/paypal/experience_context/shipping_preference&t=request"""

    GET_FROM_FILE = "GET_FROM_FILE"
    NO_SHIPPING = "NO_SHIPPING"
    SET_PROVIDED_ADDRESS = "SET_PROVIDED_ADDRESS"


class LandingPageEnum(enum.StrEnum):
    """https://developer.paypal.com/docs/api/orders/v2/#orders_create!path=payment_source/paypal/experience_context/shipping_preference&t=request"""

    LOGIN = "LOGIN"
    GUEST_CHECKOUT = "GUEST_CHECKOUT"
    NO_PREFERENCE = "NO_PREFERENCE"


class UserActionEnum(enum.StrEnum):
    """https://developer.paypal.com/docs/api/orders/v2/#orders_create!path=payment_source/paypal/experience_context/user_action&t=request"""

    CONTINUE = "CONTINUE"
    PAY_NOW = "PAY_NOW"


class PaymentMethodPreferenceEnum(enum.StrEnum):
    """https://developer.paypal.com/docs/api/orders/v2/#orders_create!path=payment_source/paypal/experience_context/payment_method_preference&t=request"""

    UNRESTRICTED = "UNRESTRICTED"
    IMMEDIATE_PAYMENT_REQUIRED = "IMMEDIATE_PAYMENT_REQUIRED"


@dataclass
class PayPalExperienceContext:
    payment_method_preference: PaymentMethodPreferenceEnum
    brand_name: str
    locale: str
    landing_page: LandingPageEnum
    shipping_preference: ShippingPreferenceEnum
    user_action: UserActionEnum
    return_url: str
    cancel_url: str


class OrderIntentEnum(enum.StrEnum):
    CAPTURE = "CAPTURE"
    AUTHORIZE = "AUTHORIZE"


@dataclass
class Order:
    intent: OrderIntentEnum
    purchase_units: list[PurchaseUnit]
    experience_context: PayPalExperienceContext


class PayPalStatusEnum(enum.StrEnum):
    CREATED = "CREATED"
    SAVED = "SAVED"
    APPROVED = "APPROVED"
    VOIDED = "VOIDED"
    COMPLETED = "COMPLETED"
    PAYER_ACTION_REQUIRED = "PAYER_ACTION_REQUIRED"
