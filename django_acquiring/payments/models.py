from uuid import uuid4

import django.db.models

from django_acquiring.payments import domain
from django_acquiring.protocols.payments import AbstractPaymentAttempt, AbstractPaymentMethod, AbstractPaymentOperation


class PaymentAttempt(django.db.models.Model):
    created_at = django.db.models.DateTimeField(auto_now_add=True)

    # https://docs.djangoproject.com/en/5.0/ref/models/fields/#uuidfield
    id = django.db.models.UUIDField(primary_key=True, default=uuid4, editable=False)

    def __str__(self) -> str:
        return f"PaymentAttempt[id={self.id}]"

    def to_domain(self) -> AbstractPaymentAttempt:
        return domain.PaymentAttempt(
            id=self.id,
            created_at=self.created_at,
            payment_methods=[payment_method.to_domain() for payment_method in self.payment_methods.all()],
        )


class PaymentMethod(django.db.models.Model):
    created_at = django.db.models.DateTimeField(auto_now_add=True)

    # https://docs.djangoproject.com/en/5.0/ref/models/fields/#uuidfield
    id = django.db.models.UUIDField(primary_key=True, default=uuid4, editable=False)

    payment_attempt = django.db.models.ForeignKey(
        PaymentAttempt,
        on_delete=django.db.models.CASCADE,
        related_name="payment_methods",
    )

    confirmable = django.db.models.BooleanField(
        editable=False,
        help_text="Whether this PaymentMethod can at some point run inside PaymentFlow.confirm",
    )

    def __str__(self) -> str:
        return f"PaymentMethod[id={self.id}]"

    def to_domain(self) -> AbstractPaymentMethod:
        return domain.PaymentMethod(
            id=self.id,
            created_at=self.created_at,
            payment_attempt_id=self.payment_attempt_id,
            payment_operations=[payment_operation.to_domain() for payment_operation in self.payment_operations.all()],
            confirmable=self.confirmable,
        )


class PaymentOperationTypeChoices(django.db.models.TextChoices):
    initialize = "initialize"
    process_actions = "process_actions"
    pay = "pay"
    confirm = "confirm"
    refund = "refund"
    after_pay = "after_pay"
    after_confirm = "after_confirm"
    after_refund = "after_refund"


class PaymentOperationStatusChoices(django.db.models.TextChoices):
    started = "started"
    failed = "failed"
    completed = "completed"
    requires_action = "requires_action"
    pending = "pending"


# TODO Add failure reason to Payment Operation as an optional string


class PaymentOperation(django.db.models.Model):
    created_at = django.db.models.DateTimeField(auto_now_add=True)

    type = django.db.models.CharField(max_length=16, choices=PaymentOperationTypeChoices)
    status = django.db.models.CharField(max_length=15, choices=PaymentOperationStatusChoices)
    payment_method = django.db.models.ForeignKey(
        PaymentMethod,
        on_delete=django.db.models.CASCADE,
        related_name="payment_operations",
    )

    def __str__(self) -> str:
        return f"PaymentOperation[type={self.type}, status={self.status}]"

    def to_domain(self) -> AbstractPaymentOperation:
        return domain.PaymentOperation(
            type=self.type,
            status=self.status,
            payment_method_id=self.payment_method_id,
        )
