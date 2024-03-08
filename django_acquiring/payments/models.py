from uuid import uuid4

from django.db import models

from .domain import PaymentAttempt as DomainPaymentAttempt
from .domain import PaymentMethod as DomainPaymentMethod
from .domain import StageEvent as DomainStageEvent


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
            payment_methods=[payment_method.to_domain() for payment_method in self.payment_methods.all()],
        )


class PaymentMethod(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)

    # https://docs.djangoproject.com/en/5.0/ref/models/fields/#uuidfield
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)

    payment_attempt = models.ForeignKey(PaymentAttempt, on_delete=models.CASCADE, related_name="payment_methods")

    def __str__(self) -> str:
        return f"PaymentMethod[id={self.id}]"

    def to_domain(self) -> DomainPaymentMethod:
        return DomainPaymentMethod(
            id=self.id,
            created_at=self.created_at,
            payment_attempt_id=self.payment_attempt_id,
            stage_events=[stage_event.to_domain() for stage_event in self.stage_events.all()],
        )


class StageEventNameChoices(models.TextChoices):
    authenticate = "authenticate"
    authorize = "authorize"
    charge = "charge"
    void = "void"
    refund = "refund"
    synchronize = "synchronize"
    mark_as_canceled = "mark_as_canceled"


class StageEventStatusChoices(models.TextChoices):
    started = "started"
    failed = "failed"
    completed = "completed"
    requires_action = "requires_action"


class StageEvent(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)

    name = models.CharField(max_length=16, choices=StageEventNameChoices)
    status = models.CharField(max_length=15, choices=StageEventStatusChoices)
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.CASCADE, related_name="stage_events")

    def __str__(self) -> str:
        return f"StageEvent[name={self.name}, status={self.status}]"

    def to_domain(self) -> DomainStageEvent:
        return DomainStageEvent(
            name=self.name,
            status=self.status,
            payment_method_id=self.payment_method_id,
        )
