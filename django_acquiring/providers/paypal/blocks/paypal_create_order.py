import os
import uuid
from dataclasses import dataclass
from typing import Sequence

from django_acquiring.domain import BlockResponse, wrapped_by_block_events
from django_acquiring.enums import OperationStatusEnum
from django_acquiring.protocols import AbstractBlock, AbstractBlockResponse, AbstractPaymentMethod

from ..adapter import PayPalAdapter
from ..domain import (
    LandingPageEnum,
    Order,
    OrderIntentEnum,
    PaymentMethodPreferenceEnum,
    PayPalExperienceContext,
    ShippingPreferenceEnum,
    UserActionEnum,
)


@dataclass
class PayPalCreateOrderBlock:
    adapter: PayPalAdapter = PayPalAdapter(
        base_url=os.environ["PAYPAL_BASE_URL"],
        client_id=os.environ["PAYPAL_CLIENT_ID"],
        client_secret=os.environ["PAYPAL_CLIENT_SECRET"],
    )

    @wrapped_by_block_events
    def run(self, payment_method: AbstractPaymentMethod, *args: Sequence, **kwargs: dict) -> AbstractBlockResponse:
        transaction_id = uuid.uuid4()
        order = Order(
            intent=OrderIntentEnum.CAPTURE,
            purchase_units=[],
            experience_context=PayPalExperienceContext(
                payment_method_preference=PaymentMethodPreferenceEnum.IMMEDIATE_PAYMENT_REQUIRED,
                brand_name="ACME, Inc",
                locale="en-US",
                landing_page=LandingPageEnum.LOGIN,
                user_action=UserActionEnum.CONTINUE,
                return_url="https://example.com/returnUrl",
                cancel_url="https://example.com/cancelUrl",
                shipping_preference=ShippingPreferenceEnum.NO_SHIPPING,
            ),
        )
        self.adapter.create_order(
            request_id=transaction_id,
            order=order,
        )

        return BlockResponse(status=OperationStatusEnum.COMPLETED, actions=[])


assert issubclass(PayPalCreateOrderBlock, AbstractBlock)
