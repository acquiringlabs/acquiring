from uuid import UUID

from django_acquiring.payments.domain import PaymentAttempt as DomainPaymentAttempt
from django_acquiring.payments.domain import PaymentMethod as DomainPaymentMethod
from django_acquiring.payments.models import PaymentAttempt as DbPaymentAttempt
from django_acquiring.payments.models import PaymentMethod as DbPaymentMethod
from django_acquiring.payments.models import PaymentOperation as DbPaymentOperation
from django_acquiring.protocols.payments import (
    AbstractPaymentAttempt,
    AbstractPaymentMethod,
    AbstractPaymentOperation,
    PaymentOperationStatusEnum,
    PaymentOperationTypeEnum,
)


class PaymentAttemptRepository:
    def add(self, data: dict) -> AbstractPaymentAttempt:
        payment_attempt = DbPaymentAttempt()
        payment_attempt.save()
        return payment_attempt.to_domain()

    def get(self, id: UUID) -> AbstractPaymentAttempt:
        try:
            payment_attempt = DbPaymentAttempt.objects.prefetch_related(
                "payment_methods", "payment_methods__payment_operations"
            ).get(id=id)
            return payment_attempt.to_domain()
        except DbPaymentAttempt.DoesNotExist:
            raise DomainPaymentAttempt.DoesNotExist


class PaymentMethodRepository:
    def add(self, data: dict) -> AbstractPaymentMethod:
        db_payment_method = DbPaymentMethod(
            payment_attempt_id=data["payment_attempt_id"],
        )
        db_payment_method.save()
        return db_payment_method.to_domain()

    def get(self, id: UUID) -> AbstractPaymentMethod:
        try:
            payment_attempt = DbPaymentMethod.objects.prefetch_related("payment_operations").get(id=id)
            return payment_attempt.to_domain()
        except DbPaymentMethod.DoesNotExist:
            raise DomainPaymentMethod.DoesNotExist


class PaymentOperationRepository:

    def add(
        self, payment_method: AbstractPaymentMethod, type: PaymentOperationTypeEnum, status: PaymentOperationStatusEnum
    ) -> AbstractPaymentOperation:
        db_payment_operation = DbPaymentOperation(
            payment_method_id=payment_method.id,
            type=type,
            status=status,
        )
        db_payment_operation.save()
        payment_operation = db_payment_operation.to_domain()
        payment_method.payment_operations.append(payment_operation)
        return payment_operation

    def get(self, id: UUID): ...
