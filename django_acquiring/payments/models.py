from uuid import uuid4

from django.db import models

from .domain import PaymentAttempt as DomainPaymentAttempt


class PaymentAttempt(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)

    # https://docs.djangoproject.com/en/5.0/ref/models/fields/#uuidfield
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)

    def __str__(self) -> str:
        return f"PaymentAttempt[id={self.id}]"

    def to_domain(self) -> DomainPaymentAttempt:
        return DomainPaymentAttempt(
            id=self.id,
            created_at=self.created_at,
        )
