import uuid
from dataclasses import dataclass
from typing import TYPE_CHECKING, Sequence

from django_acquiring import domain, enums, repositories

from ..adapter import PayPalAdapter
from ..domain import Amount, Order, OrderIntentEnum, PayPalStatusEnum, PurchaseUnit

if TYPE_CHECKING:
    from django_acquiring import protocols


@dataclass
class PayPalCreateOrder:
    adapter: PayPalAdapter

    @domain.wrapped_by_block_events(repository=repositories.BlockEventRepository())
    def run(
        self, payment_method: "protocols.AbstractPaymentMethod", *args: Sequence, **kwargs: dict
    ) -> "protocols.AbstractBlockResponse":
        external_id = uuid.uuid4()

        items = payment_method.payment_attempt.items
        order = Order(
            intent=OrderIntentEnum.CAPTURE,
            purchase_units=[
                PurchaseUnit(
                    reference_id=item.reference,
                    amount=Amount(
                        currency_code=payment_method.payment_attempt.currency,
                        value=str(item.quantity),
                    ),
                )
                for item in items
            ],
        )
        response = self.adapter.create_order(
            payment_method=payment_method,
            request_id=external_id,
            order=order,
        )

        if response.status == PayPalStatusEnum.FAILED:
            return domain.BlockResponse(
                status=enums.OperationStatusEnum.FAILED,
                actions=[],
                error_message=str(response.raw_data),
            )

        parsed_data = self._parse_response_data(response.raw_data)

        return domain.BlockResponse(
            status=enums.OperationStatusEnum.COMPLETED,
            actions=[{"redirect_url": parsed_data["redirect_url"]}],  # TODO Convert Action to dataclass
        )

    def _parse_response_data(self, data: dict) -> dict:
        return {"redirect_url": next((link["href"] for link in data["links"] if link["rel"] == "approve"))}