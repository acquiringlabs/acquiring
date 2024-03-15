from django.db import models
from django_acquiring.payments.models import PaymentMethod
from django_acquiring.protocols.events import AbstractBlockEvent
from .domain import BlockEvent as DomainBlockEvent


class BlockEventStatusChoices(models.TextChoices):
    started = "started"
    failed = "failed"
    completed = "completed"
    requires_action = "requires_action"
    pending = "pending"


class BlockEvent(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=15, choices=BlockEventStatusChoices)
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.CASCADE)
    block_name = models.CharField(max_length=20)

    def __str__(self) -> str:
        return f"PaymentAttempt[id={self.id}]"

    def to_domain(self) -> AbstractBlockEvent:
        return DomainBlockEvent(
            status=self.status,
            payment_method_id=self.payment_method.id,
            block_name=self.block_name,
        )
