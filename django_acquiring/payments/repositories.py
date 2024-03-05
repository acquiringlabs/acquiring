from .domain import PaymentAttempt
from .models import PaymentAttempt as DbPaymentAttempt
from uuid import UUID


class PaymentRepository:
    def add(self, data: dict) -> PaymentAttempt:
        payment_attempt = DbPaymentAttempt()
        payment_attempt.save()
        return payment_attempt.to_domain()

    def get(self, id: UUID) -> PaymentAttempt | None:
        try:
            payment_attempt = DbPaymentAttempt.objects.get(id=id)
            return payment_attempt.to_domain()
        except DbPaymentAttempt.DoesNotExist:
            return None
