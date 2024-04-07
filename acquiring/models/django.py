from typing import TYPE_CHECKING
from uuid import uuid4

import django.db.models
from django.core import validators as django_validators

from acquiring import domain

if TYPE_CHECKING:
    from acquiring import protocols


CURRENCY_CODE_MAX_LENGTH = 3


class Identifiable(django.db.models.Model):
    """Mixin for models that can be identified"""

    created_at = django.db.models.DateTimeField(auto_now_add=True)

    # https://docs.djangoproject.com/en/5.0/ref/models/fields/#uuidfield
    id = django.db.models.UUIDField(primary_key=True, default=uuid4, editable=False)

    class Meta:
        abstract = True


class PaymentAttempt(Identifiable, django.db.models.Model):

    # https://en.wikipedia.org/wiki/ISO_4217
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
            created_at=self.created_at,
            amount=self.amount,
            currency=self.currency,
            items=[item.to_domain() for item in self.items.all()],
            payment_method_ids=[payment_method.id for payment_method in self.payment_methods.all()],
        )

    # TODO Verify that total amount by items equals amount of the PaymentAttempt


class Item(Identifiable, django.db.models.Model):

    payment_attempt = django.db.models.ForeignKey(
        PaymentAttempt,
        on_delete=django.db.models.CASCADE,
        related_name="items",
    )

    name = django.db.models.TextField()

    quantity = django.db.models.PositiveSmallIntegerField(
        help_text="Quantity of the order line item. Must be a non-negative number."
    )
    quantity_unit = django.db.models.TextField(
        help_text="Unit used to describe the quantity, e.g. kg, pcs, etc.",
        blank=True,
        null=True,
    )

    reference = django.db.models.TextField(
        help_text="Used for storing merchant's internal reference number",
    )

    unit_price = django.db.models.BigIntegerField(
        help_text=(
            "Price for a single unit of the order line. "
            "A positive integer representing how much to charge in the currency unit "
            "(e.g., 100 cents to charge $1.00 or 100 to charge ¥100, a zero-decimal currency). "
            "Currency is assumed to be the one provided in PaymentAttempt."
        )
    )

    def __str__(self) -> str:
        return f"[reference={self.reference}, quantity={self.quantity}{str(' ' + self.quantity_unit) if self.quantity_unit else ''}]"

    def to_domain(self) -> "protocols.AbstractItem":
        return domain.Item(
            id=self.id,
            created_at=self.created_at,
            payment_attempt_id=self.payment_attempt_id,
            name=self.name,
            quantity=self.quantity,
            quantity_unit=self.quantity_unit,
            reference=self.reference,
            unit_price=self.unit_price,
        )


class PaymentMethod(Identifiable, django.db.models.Model):

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
            payment_attempt=self.payment_attempt.to_domain(),
            payment_operations=[payment_operation.to_domain() for payment_operation in self.payment_operations.all()],
            confirmable=self.confirmable,
        )


class Token(django.db.models.Model):

    # TODO Rename to timestamp (it's not identifiable)
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


class StatusChoices(django.db.models.TextChoices):
    STARTED = "started"
    FAILED = "failed"
    COMPLETED = "completed"
    REQUIRES_ACTION = "requires_action"
    PENDING = "pending"
    NOT_PERFORMED = "not_performed"


# TODO Add failure reason to Payment Operation as an optional string
class PaymentOperation(django.db.models.Model):
    created_at = django.db.models.DateTimeField(auto_now_add=True)

    type = django.db.models.CharField(max_length=16, choices=PaymentOperationTypeChoices)
    status = django.db.models.CharField(max_length=15, choices=StatusChoices)
    payment_method = django.db.models.ForeignKey(
        PaymentMethod,
        on_delete=django.db.models.CASCADE,
        related_name="payment_operations",
    )

    class Meta:
        unique_together = ("status", "payment_method", "type")

    def __str__(self) -> str:
        return f"[type={self.type}, status={self.status}]"

    def to_domain(self) -> "protocols.AbstractPaymentOperation":
        return domain.PaymentOperation(
            type=self.type,
            status=self.status,
            payment_method_id=self.payment_method_id,
        )


class BlockEvent(django.db.models.Model):
    created_at = django.db.models.DateTimeField(auto_now_add=True)
    status = django.db.models.CharField(max_length=15, choices=StatusChoices)
    payment_method = django.db.models.ForeignKey(PaymentMethod, on_delete=django.db.models.CASCADE)
    block_name = django.db.models.CharField(max_length=20)

    class Meta:
        unique_together = ("status", "payment_method", "block_name")

    def __str__(self) -> str:
        return f"[{self.block_name}|status={self.status}]"

    def to_domain(self) -> "protocols.AbstractBlockEvent":
        return domain.BlockEvent(
            status=self.status,
            payment_method_id=self.payment_method.id,
            block_name=self.block_name,
        )


class Transaction(django.db.models.Model):

    external_id = django.db.models.TextField()  # No arbitrary limitations are imposed

    # Filled with Provided data on request, not auto added
    timestamp = django.db.models.DateTimeField(auto_now_add=False)

    raw_data = django.db.models.JSONField()

    provider_name = django.db.models.TextField()

    payment_method = django.db.models.ForeignKey(
        PaymentMethod,
        on_delete=django.db.models.CASCADE,
        related_name="transaction",
    )

    def __str__(self) -> str:
        return f"[provider={self.provider_name}|payment_method={self.payment_method_id}|{self.external_id}]"

    def to_domain(self) -> "protocols.AbstractTransaction":
        return domain.Transaction(
            external_id=self.external_id,
            timestamp=self.timestamp,
            raw_data=self.raw_data,
            provider_name=self.provider_name,
            payment_method_id=self.payment_method_id,
        )
