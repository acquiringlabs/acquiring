from typing import TYPE_CHECKING

from .adapter import PayPalAdapter, PayPalResponse, PayPalStatusEnum
from .blocks import PayPalCreateOrder
from .domain import Amount, Order, OrderIntentEnum, PurchaseUnit

if TYPE_CHECKING:
    from django_acquiring.domain.flow import PaymentFlow


def paypal_payment_flow() -> "PaymentFlow":
    import os

    from django_acquiring import domain, repositories

    return domain.PaymentFlow(
        payment_method_repository=repositories.PaymentMethodRepository(),
        operations_repository=repositories.PaymentOperationRepository(),
        initialize_block=None,
        process_action_block=None,
        pay_blocks=[
            PayPalCreateOrder(
                adapter=PayPalAdapter(
                    base_url=os.environ["PAYPAL_BASE_URL"],
                    callback_url=os.environ["CALLBACK_BASE_URL"],
                    client_id=os.environ["PAYPAL_CLIENT_ID"],
                    client_secret=os.environ["PAYPAL_CLIENT_SECRET"],
                )
            )
        ],
        after_pay_blocks=[],
        confirm_block=None,
        after_confirm_blocks=[],
    )


__all__ = [
    "Amount",
    "Order",
    "OrderIntentEnum",
    "PayPalAdapter",
    "PayPalCreateOrder",
    "PayPalResponse",
    "PayPalStatusEnum",
    "PurchaseUnit",
    "paypal_payment_flow",
]

assert __all__ == sorted(__all__), sorted(__all__)