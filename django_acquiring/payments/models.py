from uuid import uuid4

from django.db import models

from django_acquiring.protocols.payments import AbstractPaymentAttempt, AbstractPaymentMethod, AbstractPaymentOperation

from .domain import PaymentAttempt as DomainPaymentAttempt
from .domain import PaymentMethod as DomainPaymentMethod
from .domain import PaymentOperation as DomainPaymentOperation


class PaymentAttempt(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)

    # https://docs.djangoproject.com/en/5.0/ref/models/fields/#uuidfield
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)

    def __str__(self) -> str:
        return f"PaymentAttempt[id={self.id}]"

    def to_domain(self) -> AbstractPaymentAttempt:
        return DomainPaymentAttempt(
            id=self.id,
            created_at=self.created_at,
            payment_methods=[payment_method.to_domain() for payment_method in self.payment_methods.all()],
        )


class PaymentMethod(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)

    # https://docs.djangoproject.com/en/5.0/ref/models/fields/#uuidfield
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)

    payment_attempt = models.ForeignKey(PaymentAttempt, on_delete=models.CASCADE, related_name="payment_methods")

    def __str__(self) -> str:
        return f"PaymentMethod[id={self.id}]"

    def to_domain(self) -> AbstractPaymentMethod:
        return DomainPaymentMethod(
            id=self.id,
            created_at=self.created_at,
            payment_attempt_id=self.payment_attempt_id,
            payment_operations=[payment_operation.to_domain() for payment_operation in self.payment_operations.all()],
        )


class PaymentOperationTypeChoices(models.TextChoices):
    initialize = "initialize"
    process_actions = "process_actions"
    pay = "pay"
    void = "void"
    refund = "refund"
    mark_as_canceled = "mark_as_canceled"


class PaymentOperationStatusChoices(models.TextChoices):
    started = "started"
    failed = "failed"
    completed = "completed"
    requires_action = "requires_action"
    pending = "pending"


# TODO Add failure reason to Payment Operation as an optional string


class PaymentOperation(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)

    type = models.CharField(max_length=16, choices=PaymentOperationTypeChoices)
    status = models.CharField(max_length=15, choices=PaymentOperationStatusChoices)
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.CASCADE, related_name="payment_operations")

    def __str__(self) -> str:
        return f"PaymentOperation[type={self.type}, status={self.status}]"

    def to_domain(self) -> AbstractPaymentOperation:
        return DomainPaymentOperation(
            type=self.type,
            status=self.status,
            payment_method_id=self.payment_method_id,
        )
