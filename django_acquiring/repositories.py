from uuid import UUID

from django_acquiring import domain, models
from django_acquiring.protocols import events
from django_acquiring.protocols.enums import OperationStatusEnum, OperationTypeEnum
from django_acquiring.protocols.payments import (
    AbstractDraftPaymentAttempt,
    AbstractDraftPaymentMethod,
    AbstractPaymentAttempt,
    AbstractPaymentMethod,
    AbstractPaymentOperation,
)


class PaymentAttemptRepository:
    def add(self, data: AbstractDraftPaymentAttempt) -> AbstractPaymentAttempt:
        payment_attempt = models.PaymentAttempt(
            order_id=data.order_id,
        )
        payment_attempt.save()
        return payment_attempt.to_domain()

    def get(self, id: UUID) -> AbstractPaymentAttempt:
        try:
            payment_attempt = (
                models.PaymentAttempt.objects.prefetch_related("payment_methods", "payment_methods__payment_operations")
                .select_related("order")
                .get(id=id)
            )
            return payment_attempt.to_domain()
        except models.PaymentAttempt.DoesNotExist:
            raise domain.PaymentAttempt.DoesNotExist


class PaymentMethodRepository:
    def add(self, data: AbstractDraftPaymentMethod) -> AbstractPaymentMethod:
        db_payment_method = models.PaymentMethod(
            payment_attempt_id=data.payment_attempt_id,
            confirmable=data.confirmable,
        )
        db_payment_method.save()
        return db_payment_method.to_domain()

    def get(self, id: UUID) -> AbstractPaymentMethod:
        try:
            payment_method = models.PaymentMethod.objects.prefetch_related("payment_operations").get(id=id)
            return payment_method.to_domain()
        except models.PaymentMethod.DoesNotExist:
            raise domain.PaymentMethod.DoesNotExist


class PaymentOperationRepository:

    def add(
        self,
        payment_method: AbstractPaymentMethod,
        type: OperationTypeEnum,
        status: OperationStatusEnum,
    ) -> AbstractPaymentOperation:
        db_payment_operation = models.PaymentOperation(
            payment_method_id=payment_method.id,
            type=type,
            status=status,
        )
        db_payment_operation.save()
        payment_operation = db_payment_operation.to_domain()
        payment_method.payment_operations.append(payment_operation)
        return payment_operation

    def get(self, id: UUID) -> AbstractPaymentOperation: ...  # type: ignore[empty-body]


class BlockEventRepository:
    def add(self, block_event: events.AbstractBlockEvent) -> events.AbstractBlockEvent:
        block_event = models.BlockEvent(
            status=block_event.status,
            payment_method_id=block_event.payment_method_id,
            block_name=block_event.block_name,
        )
        block_event.save()
        return block_event.to_domain()

    def get(self, id: UUID) -> events.AbstractBlockEvent: ...  # type: ignore[empty-body]
