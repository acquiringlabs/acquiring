import django.db.models
from django_acquiring.payments import models
from django_acquiring.protocols.events import AbstractBlockEvent
from .domain import BlockEvent as DomainBlockEvent


class BlockEventStatusChoices(django.db.models.TextChoices):
    started = "started"
    failed = "failed"
    completed = "completed"
    requires_action = "requires_action"
    pending = "pending"


class BlockEvent(django.db.models.Model):
    created_at = django.db.models.DateTimeField(auto_now_add=True)
    status = django.db.models.CharField(max_length=15, choices=BlockEventStatusChoices)
    payment_method = django.db.models.ForeignKey(models.PaymentMethod, on_delete=django.db.models.CASCADE)
    block_name = django.db.models.CharField(max_length=20)

    def __str__(self) -> str:
        return f"PaymentAttempt[id={self.id}]"

    def to_domain(self) -> AbstractBlockEvent:
        return DomainBlockEvent(
            status=self.status,
            payment_method_id=self.payment_method.id,
            block_name=self.block_name,
        )
