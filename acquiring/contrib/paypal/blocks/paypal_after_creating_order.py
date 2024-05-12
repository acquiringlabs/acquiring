from dataclasses import dataclass

from acquiring import domain, enums, protocols
from acquiring.contrib import paypal


@dataclass
class PayPalAfterCreatingOrder:
    unit_of_work: protocols.UnitOfWork
    block_event_repository: protocols.Repository
    transaction_repository: protocols.Repository

    @domain.wrapped_by_block_events
    def run(
        self,
        payment_method: "protocols.PaymentMethod",
        webhook_data: paypal.domain.PayPalWebhookData,
    ) -> "protocols.BlockResponse":
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
