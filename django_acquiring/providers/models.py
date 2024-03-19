import django.db.models
from django_acquiring.protocols.providers import AbstractTransaction
from django_acquiring.providers import domain


class Transaction(django.db.models.Model):
    created_at = django.db.models.DateTimeField(auto_now_add=True)

    payment_method = django.db.models.ForeignKey(
        "payments.PaymentMethod",
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
