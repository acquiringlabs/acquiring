from uuid import UUID

from django_acquiring.payments import domain, models
from django_acquiring.protocols.payments import (
    AbstractPaymentAttempt,
    AbstractPaymentMethod,
    AbstractPaymentOperation,
    OperationStatusEnum,
    OperationTypeEnum,
)


class PaymentAttemptRepository:
    def add(self, data: dict) -> AbstractPaymentAttempt:
        payment_attempt = models.PaymentAttempt()
        payment_attempt.save()
        return payment_attempt.to_domain()

    def get(self, id: UUID) -> AbstractPaymentAttempt:
        try:
            payment_attempt = models.PaymentAttempt.objects.prefetch_related(
                "payment_methods", "payment_methods__payment_operations"
            ).get(id=id)
            return payment_attempt.to_domain()
        except models.PaymentAttempt.DoesNotExist:
            raise domain.PaymentAttempt.DoesNotExist


class PaymentMethodRepository:
    def add(self, data: dict) -> AbstractPaymentMethod:
        db_payment_method = models.PaymentMethod(
            payment_attempt_id=data["payment_attempt_id"],
            confirmable=data["confirmable"],
        )
        db_payment_method.save()
        return db_payment_method.to_domain()

    def get(self, id: UUID) -> AbstractPaymentMethod:
        try:
            payment_attempt = models.PaymentMethod.objects.prefetch_related("payment_operations").get(id=id)
            return payment_attempt.to_domain()
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
