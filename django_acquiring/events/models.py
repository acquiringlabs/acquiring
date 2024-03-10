from django.db import models
from django_acquiring.payments.models import PaymentMethod
from django_acquiring.protocols.events import AbstractBlockEvent
from .domain import BlockEvent as DomainBlockEvent


class BlockEvent(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    success = models.BooleanField()
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.CASCADE)
    block_name = models.CharField(max_length=20)

    def __str__(self) -> str:
        return f"PaymentAttempt[id={self.id}]"

    def to_domain(self) -> AbstractBlockEvent:
        return DomainBlockEvent(
            success=self.success,
            payment_method_id=self.payment_method.id,
            block_name=self.block_name,
        )
