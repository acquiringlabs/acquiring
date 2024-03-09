from uuid import UUID

from .domain import PaymentAttempt, PaymentMethod, PaymentOperation
from .models import PaymentAttempt as DbPaymentAttempt
from .models import PaymentMethod as DbPaymentMethod
from .models import PaymentOperation as DbPaymentOperation
from .protocols import OperationStatusEnum, PaymentOperationTypeEnum


class PaymentAttemptRepository:
    def add(self, data: dict) -> PaymentAttempt:
        payment_attempt = DbPaymentAttempt()
        payment_attempt.save()
        return payment_attempt.to_domain()

    def get(self, id: UUID) -> PaymentAttempt | None:
        try:
            payment_attempt = DbPaymentAttempt.objects.prefetch_related(
                "payment_methods", "payment_methods__payment_operations"
            ).get(id=id)
            return payment_attempt.to_domain()
        except DbPaymentAttempt.DoesNotExist:
            return None


class PaymentMethodRepository:
    def add(self, data: dict) -> PaymentMethod:
        db_payment_method = DbPaymentMethod(
            payment_attempt_id=data["payment_attempt_id"],
        )
        db_payment_method.save()
        return db_payment_method.to_domain()

    def get(self, id: UUID) -> PaymentMethod | None:
        try:
            payment_attempt = DbPaymentMethod.objects.prefetch_related("payment_operations").get(id=id)
            return payment_attempt.to_domain()
        except DbPaymentMethod.DoesNotExist:
            return None

    def add_payment_operation(
        self, payment_method: PaymentMethod, type: PaymentOperationTypeEnum, status: OperationStatusEnum
    ) -> PaymentOperation:
        db_payment_operation = DbPaymentOperation(
            payment_method_id=payment_method.id,
            type=type,
            status=status,
        )
        db_payment_operation.save()
        payment_operation = db_payment_operation.to_domain()
        payment_method.payment_operations.append(payment_operation)
        return payment_operation
