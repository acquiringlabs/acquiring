from uuid import UUID

import deal

from acquiring import domain, enums, protocols
from acquiring.storage.django import models


class PaymentAttemptRepository:

    def add(self, data: "protocols.DraftPaymentAttempt") -> "protocols.PaymentAttempt": ...  # type: ignore[empty-body]

    @deal.reason(
        domain.PaymentAttempt.DoesNotExist,
        lambda _, id: models.PaymentAttempt.objects.filter(id=id).count() == 0,
    )
    def get(self, id: UUID) -> "protocols.PaymentAttempt":
        try:
            payment_attempt = models.PaymentAttempt.objects.prefetch_related("payment_methods").get(id=id)
            return payment_attempt.to_domain()
        except models.PaymentAttempt.DoesNotExist:
            raise domain.PaymentAttempt.DoesNotExist


class PaymentMethodRepository:

    @deal.safe
    def add(self, data: "protocols.DraftPaymentMethod") -> "protocols.PaymentMethod":
        db_payment_method = models.PaymentMethod(
            payment_attempt_id=data.payment_attempt_id,
        )
        db_payment_method.save()
        return db_payment_method.to_domain()

    @deal.reason(
        domain.PaymentMethod.DoesNotExist,
        lambda _, id: models.PaymentMethod.objects.filter(id=id).count() == 0,
    )
    def get(self, id: UUID) -> "protocols.PaymentMethod":
        try:
            payment_method = models.PaymentMethod.objects.prefetch_related("operation_events", "tokens").get(id=id)
            return payment_method.to_domain()
        except models.PaymentMethod.DoesNotExist:
            raise domain.PaymentMethod.DoesNotExist


class OperationEventRepository:

    @deal.safe
    def add(
        self,
        payment_method: "protocols.PaymentMethod",
        type: enums.OperationTypeEnum,
        status: enums.OperationStatusEnum,
    ) -> "protocols.OperationEvent":
        db_operation_event = models.OperationEvent(
            payment_method_id=payment_method.id,
            type=type,
            status=status,
        )
        db_operation_event.save()
        operation_event = db_operation_event.to_domain()
        payment_method.operation_events.append(operation_event)
        return operation_event

    def get(self, id: UUID) -> "protocols.OperationEvent": ...  # type: ignore[empty-body]


class MilestoneRepository:

    @deal.reason(
        domain.PaymentMethod.DoesNotExist,
        lambda _, payment_method, type: models.PaymentMethod.objects.filter(id=payment_method.id).count() == 0,
    )
    @deal.reason(
        domain.PaymentAttempt.DoesNotExist,
        lambda _, payment_method, type: models.PaymentAttempt.objects.filter(
            id=payment_method.payment_attempt_id
        ).count()
        == 0,
    )
    def add(
        self,
        payment_method: "protocols.PaymentMethod",
        type: enums.AtemptStatusEnum,
    ) -> "protocols.Milestone":
        try:
            db_milestone = models.Milestone(
                payment_method_id=payment_method.id,
                payment_attempt_id=payment_method.payment_attempt_id,
                type=type,
            )
            db_milestone.save()
            return db_milestone.to_domain()
        except models.PaymentMethod.DoesNotExist:
            raise domain.PaymentMethod.DoesNotExist
        except models.PaymentAttempt.DoesNotExist:
            raise domain.PaymentAttempt.DoesNotExist

    def get(self, id: UUID) -> "protocols.Milestone": ...  # type:ignore[empty-body]


class BlockEventRepository:

    @deal.reason(
        ValueError,
        lambda self, payment_method, block_event: block_event.payment_method_id != payment_method.id,
    )
    def add(
        self, payment_method: "protocols.PaymentMethod", block_event: "protocols.BlockEvent"
    ) -> "protocols.BlockEvent":
        if block_event.payment_method_id != payment_method.id:
            raise ValueError("BlockEvent is not associated with provided PaymentMethod")
        db_block_event = models.BlockEvent(
            status=block_event.status,
            payment_method_id=payment_method.id,
            block_name=block_event.block_name,
        )
        db_block_event.save()
        return db_block_event.to_domain()

    def get(self, id: UUID) -> "protocols.BlockEvent": ...  # type: ignore[empty-body]


# TODO Append transaction to payment_method.transactions?
# TODO Test when payment method id does not correspond to any existing payment method
class TransactionRepository:

    @deal.safe
    def add(
        self,
        transaction: "protocols.Transaction",
    ) -> "protocols.Transaction":
        db_transaction = models.Transaction(
            external_id=transaction.external_id,
            timestamp=transaction.timestamp,
            raw_data=transaction.raw_data,
            provider_name=transaction.provider_name,
            payment_method_id=transaction.payment_method_id,
        )
        db_transaction.save()
        return db_transaction.to_domain()

    def get(self, id: UUID) -> "protocols.Transaction": ...  # type: ignore[empty-body]


class TokenRepository:

    @deal.reason(
        domain.Token.DoesNotExist,
        lambda _, token: models.Token.objects.filter(token=token).count() == 0,
    )
    def get(self, token: str) -> "protocols.PaymentMethod":
        try:
            instance = models.Token.objects.select_related("token").get(token=token)
            return instance.to_domain()
        except models.Token.DoesNotExist:
            raise domain.Token.DoesNotExist

    @deal.reason(
        domain.PaymentMethod.DoesNotExist,
        lambda _, payment_method, token: models.PaymentMethod.objects.filter(id=payment_method.id).count() == 0,
    )
    def add(self, payment_method: "protocols.PaymentMethod", token: "protocols.Token") -> "protocols.PaymentMethod":
        try:
            db_payment_method = models.PaymentMethod.objects.get(id=payment_method.id)
        except models.PaymentMethod.DoesNotExist:
            raise domain.PaymentMethod.DoesNotExist

        db_token = models.Token(
            payment_method=db_payment_method,
            timestamp=token.timestamp,  # TODO Ensure via type that datetime is timezone aware
            token=token.token,
            expires_at=token.expires_at,  # TODO Ensure via type that datetime is timezone aware
            fingerprint=token.fingerprint,
            metadata=token.metadata,
        )
        db_token.save()

        payment_method.tokens.append(db_token.to_domain())
        return payment_method
