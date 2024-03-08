from uuid import UUID

from .domain import PaymentAttempt, PaymentMethod
from .models import PaymentAttempt as DbPaymentAttempt
from .models import PaymentMethod as DbPaymentMethod


class PaymentAttemptRepository:
    def add(self, data: dict) -> PaymentAttempt:
        payment_attempt = DbPaymentAttempt()
        payment_attempt.save()
        return payment_attempt.to_domain()

    def get(self, id: UUID) -> PaymentAttempt | None:
        try:
            payment_attempt = DbPaymentAttempt.objects.prefetch_related(
                "payment_methods", "payment_methods__stage_events"
            ).get(id=id)
            return payment_attempt.to_domain()
        except DbPaymentAttempt.DoesNotExist:
            return None


class PaymentMethodRepository:
    def add(self, data: dict) -> PaymentMethod:
        payment_method = DbPaymentMethod(
            payment_attempt_id=data["payment_attempt_id"],
        )
        payment_method.save()
        return payment_method.to_domain()

    def get(self, id: UUID) -> PaymentMethod | None:
        try:
            payment_attempt = DbPaymentMethod.objects.prefetch_related("stage_events").get(id=id)
            return payment_attempt.to_domain()
        except DbPaymentMethod.DoesNotExist:
            return None
