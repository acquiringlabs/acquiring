from django_acquiring.payments.protocols import AbstractPaymentAttempt


def can_authenticate(payment_attempt: AbstractPaymentAttempt) -> bool:
    return True
