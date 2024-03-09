from django_acquiring.payments.protocols import AbstractPaymentMethod


def can_authenticate(payment_attempt: AbstractPaymentMethod) -> bool:
    return True
