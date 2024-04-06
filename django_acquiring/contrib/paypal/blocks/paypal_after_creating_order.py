from dataclasses import dataclass

from django_acquiring import domain, enums, protocols
from django_acquiring.contrib import paypal


@dataclass
class PayPalAfterCreatingOrder:
    transaction_repository: protocols.AbstractRepository

    # TODO block_event_repo is taken from block, not as an argument
    # @domain.wrapped_by_block_events(block_event_repository=repositories.django.BlockEventRepository())
    def run(
        self,
        payment_method: "protocols.AbstractPaymentMethod",
        webhook_data: paypal.domain.PayPalWebhookData,
    ) -> "protocols.AbstractBlockResponse":
        self.transaction_repository.add(
            domain.Transaction(
                external_id=webhook_data.id,
                timestamp=webhook_data.create_time,
                raw_data=webhook_data.raw_data,
                provider_name="paypal",
                payment_method_id=payment_method.id,
            )
        )

        if webhook_data.event_type == "CHECKOUT.ORDER.APPROVED":
            return domain.BlockResponse(
                status=enums.OperationStatusEnum.COMPLETED,
                actions=[],
                error_message=None,
            )

        return domain.BlockResponse(
            status=enums.OperationStatusEnum.FAILED,
            actions=[],
            error_message=f"Event Type {webhook_data.event_type} was not processed",
        )
