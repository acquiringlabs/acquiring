from uuid import uuid4

import django.db.models

from django_acquiring import domain
from django_acquiring.protocols.events import AbstractBlockEvent
from django_acquiring.protocols.orders import AbstractOrder
from django_acquiring.protocols.payments import AbstractPaymentAttempt, AbstractPaymentMethod, AbstractPaymentOperation
from django_acquiring.protocols.providers import AbstractTransaction


class Order(django.db.models.Model):
    created_at = django.db.models.DateTimeField(auto_now_add=True)

    # https://docs.djangoproject.com/en/5.0/ref/models/fields/#uuidfield
    id = django.db.models.UUIDField(primary_key=True, default=uuid4, editable=False)

    def __str__(self) -> str:
        return f"Order[id={self.id}]"

    def to_domain(self) -> AbstractOrder:
        return domain.Order(
            id=self.id,
            created_at=self.created_at,
            payment_attempts=self.payment_attempts,
        )


class PaymentAttempt(django.db.models.Model):
    created_at = django.db.models.DateTimeField(auto_now_add=True)

    # https://docs.djangoproject.com/en/5.0/ref/models/fields/#uuidfield
    id = django.db.models.UUIDField(primary_key=True, default=uuid4, editable=False)

    order = django.db.models.ForeignKey(
        Order,
        on_delete=django.db.models.CASCADE,
        related_name="payment_attempts",
    )

    def __str__(self) -> str:
        return f"PaymentAttempt[id={self.id}]"

    def to_domain(self) -> AbstractPaymentAttempt:
        return domain.PaymentAttempt(
            id=self.id,
            order_id=self.order.id,
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


class BlockEventStatusChoices(django.db.models.TextChoices):
    started = "started"
    failed = "failed"
    completed = "completed"
    requires_action = "requires_action"
    pending = "pending"


class BlockEvent(django.db.models.Model):
    created_at = django.db.models.DateTimeField(auto_now_add=True)
    status = django.db.models.CharField(max_length=15, choices=BlockEventStatusChoices)
    payment_method = django.db.models.ForeignKey(PaymentMethod, on_delete=django.db.models.CASCADE)
    block_name = django.db.models.CharField(max_length=20)

    def __str__(self) -> str:
        return f"PaymentAttempt[id={self.id}]"

    def to_domain(self) -> AbstractBlockEvent:
        return domain.BlockEvent(
            status=self.status,
            payment_method_id=self.payment_method.id,
            block_name=self.block_name,
        )


class Transaction(django.db.models.Model):
    created_at = django.db.models.DateTimeField(auto_now_add=True)

    payment_method = django.db.models.ForeignKey(
        PaymentMethod,
        on_delete=django.db.models.CASCADE,
        related_name="transaction",
    )

    provider_name = django.db.models.TextField()

    raw_data = django.db.models.JSONField()

    def __str__(self) -> str:
        return f"Transaction[id={self.provider_name}]"

    def to_domain(self) -> AbstractTransaction:
        return domain.Transaction(
            created_at=self.created_at,
            provider_name=self.provider_name,
            payment_method_id=self.payment_method_id,
            raw_data=self.raw_data,
        )
