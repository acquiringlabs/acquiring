from typing import TYPE_CHECKING
from uuid import uuid4

import django.db.models
from django.core import validators as django_validators

from django_acquiring import domain

if TYPE_CHECKING:
    from django_acquiring import protocols


CURRENCY_CODE_MAX_LENGTH = 3


class Order(django.db.models.Model):
    created_at = django.db.models.DateTimeField(auto_now_add=True)

    # https://docs.djangoproject.com/en/5.0/ref/models/fields/#uuidfield
    id = django.db.models.UUIDField(primary_key=True, default=uuid4, editable=False)

    def __str__(self) -> str:
        return f"[id={self.id}]"

    def to_domain(self) -> "protocols.AbstractOrder":
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

    # https://stackoverflow.com/questions/224462/storing-money-in-a-decimal-column-what-precision-and-scale/224866#224866
    # https://sqlblog.org/2008/04/27/performance-storage-comparisons-money-vs-decimal
    amount = django.db.models.BigIntegerField(
        help_text=(
            "Amount intended to be collected. "
            "A positive integer representing how much to charge in the currency unit "
            "(e.g., 100 cents to charge $1.00 or 100 to charge ¥100, a zero-decimal currency)."
        )
    )
    currency = django.db.models.CharField(
        max_length=CURRENCY_CODE_MAX_LENGTH,
        validators=[
            django_validators.MinLengthValidator(CURRENCY_CODE_MAX_LENGTH),
        ],
    )

    def __str__(self) -> str:
        return f"[id={self.id}, {self.currency}{self.amount}]"

    def to_domain(self) -> "protocols.AbstractPaymentAttempt":
        return domain.PaymentAttempt(
            id=self.id,
            order_id=self.order.id,
            created_at=self.created_at,
            amount=self.amount,
            currency=self.currency,
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

    token = django.db.models.OneToOneField(
        "Token",
        on_delete=django.db.models.PROTECT,
        null=True,
        blank=True,
        related_name="payment_method",
    )

    confirmable = django.db.models.BooleanField(
        editable=False,
        help_text="Whether this PaymentMethod can at some point run inside PaymentFlow.confirm",
    )

    def __str__(self) -> str:
        return f"[id={self.id}]"

    def to_domain(self) -> "protocols.AbstractPaymentMethod":
        return domain.PaymentMethod(
            id=self.id,
            created_at=self.created_at,
            token=self.token.to_domain() if self.token else None,
            payment_attempt_id=self.payment_attempt_id,
            payment_operations=[payment_operation.to_domain() for payment_operation in self.payment_operations.all()],
            confirmable=self.confirmable,
        )


class Token(django.db.models.Model):
    created_at = django.db.models.DateTimeField()  # when a token gets created is passed by the Tokenization provider
    expires_at = django.db.models.DateTimeField(null=True, blank=True)
    token = django.db.models.TextField()  # No arbitrary limitations are imposed

    fingerprint = django.db.models.TextField(
        null=True,
        blank=True,
        help_text="Fingerprinting provides a way to correlate multiple tokens together that contain the same data without needing access to the underlying data.",
    )

    metadata = django.db.models.JSONField(
        null=True,
        blank=True,
        help_text="tag your tokens with custom key-value attributes (i.e., to reference a record in your own database, tag records that fall into certain compliance requirements like GDPR, etc)",
    )

    def __str__(self) -> str:
        return f"[{self.token}]"

    def to_domain(self) -> "protocols.AbstractToken":
        return domain.Token(
            created_at=self.created_at,
            expires_at=self.expires_at,
            token=self.token,
            fingerprint=self.fingerprint,
            metadata=self.metadata,
        )


class PaymentOperationTypeChoices(django.db.models.TextChoices):
    INITIALIZE = "initialize"
    PROCESS_ACTION = "process_action"
    PAY = "pay"
    CONFIRM = "confirm"
    REFUND = "refund"
    AFTER_PAY = "after_pay"
    AFTER_CONFIRM = "after_confirm"
    AFTER_REFUND = "after_refund"


class PaymentOperationStatusChoices(django.db.models.TextChoices):
    STARTED = "started"
    FAILED = "failed"
    COMPLETED = "completed"
    REQUIRES_ACTION = "requires_action"
    PENDING = "pending"


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
        return f"[type={self.type}, status={self.status}]"

    def to_domain(self) -> "protocols.AbstractPaymentOperation":
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
        return f"[{self.block_name}|status={self.status}]"

    def to_domain(self) -> "protocols.AbstractBlockEvent":
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
        return f"[id={self.provider_name}]"

    def to_domain(self) -> "protocols.AbstractTransaction":
        return domain.Transaction(
            created_at=self.created_at,
            provider_name=self.provider_name,
            payment_method_id=self.payment_method_id,
            raw_data=self.raw_data,
        )
