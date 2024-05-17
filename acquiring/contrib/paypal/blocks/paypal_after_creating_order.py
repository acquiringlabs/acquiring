from dataclasses import dataclass

from acquiring import domain, enums, protocols
from acquiring.contrib import paypal


@dataclass
class PayPalAfterCreatingOrder:

    @domain.wrapped_by_block_events
    def run(
        self,
        unit_of_work: "protocols.UnitOfWork",
        payment_method: "protocols.PaymentMethod",
        webhook_data: paypal.domain.PayPalWebhookData,
    ) -> "protocols.BlockResponse":
        with unit_of_work as uow:
            uow.transactions.add(
                domain.Transaction(
                    external_id=webhook_data.id,
                    timestamp=webhook_data.create_time,
                    raw_data=webhook_data.raw_data,
                    provider_name="paypal",
                    payment_method_id=payment_method.id,
                )
            )
            uow.commit()

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
