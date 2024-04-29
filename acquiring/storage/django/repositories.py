from uuid import UUID

import deal
import django.db.transaction

from acquiring import domain, protocols
from acquiring.enums import OperationStatusEnum, OperationTypeEnum
from acquiring.storage.django import models


class PaymentMethodRepository:

    @deal.safe()
    def add(self, data: "protocols.DraftPaymentMethod") -> "protocols.PaymentMethod":
        db_payment_method = models.PaymentMethod(
            payment_attempt_id=data.payment_attempt.id,
            confirmable=data.confirmable,
        )
        db_payment_method.save()
        return db_payment_method.to_domain()

    @deal.reason(
        domain.PaymentMethod.DoesNotExist,
        lambda _, id: models.PaymentMethod.objects.filter(id=id).count() == 0,
    )
    def get(self, id: UUID) -> "protocols.PaymentMethod":
        try:
            payment_method = (
                models.PaymentMethod.objects.prefetch_related("payment_operations", "tokens")
                .select_related("payment_attempt")
                .get(id=id)
            )
            return payment_method.to_domain()
        except models.PaymentMethod.DoesNotExist:
            raise domain.PaymentMethod.DoesNotExist


class PaymentOperationRepository:

    @deal.raises(domain.PaymentOperation.Duplicated)  # TODO Turn this into deal.reason
    def add(
        self,
        payment_method: "protocols.PaymentMethod",
        type: OperationTypeEnum,
        status: OperationStatusEnum,
    ) -> "protocols.PaymentOperation":
        db_payment_operation = models.PaymentOperation(
            payment_method_id=payment_method.id,
            type=type,
            status=status,
        )
        try:
            db_payment_operation.save()
            payment_operation = db_payment_operation.to_domain()
            payment_method.payment_operations.append(payment_operation)
            return payment_operation
        except django.db.utils.IntegrityError:
            raise domain.PaymentOperation.Duplicated

    def get(self, id: UUID) -> "protocols.PaymentOperation": ...  # type: ignore[empty-body]


# TODO Append block event to payment_method.block_events?
# TODO Test when payment method id does not correspond to any existing payment method
class BlockEventRepository:

    @deal.raises(domain.BlockEvent.Duplicated)  # TODO Turn this into deal.reason
    def add(self, block_event: "protocols.BlockEvent") -> "protocols.BlockEvent":
        try:
            db_block_event = models.BlockEvent(
                status=block_event.status,
                payment_method_id=block_event.payment_method_id,
                block_name=block_event.block_name,
            )
            db_block_event.save()
            return db_block_event.to_domain()
        except django.db.utils.IntegrityError:
            raise domain.BlockEvent.Duplicated

    def get(self, id: UUID) -> "protocols.BlockEvent": ...  # type: ignore[empty-body]


# TODO Append transaction to payment_method.transactions?
# TODO Test when payment method id does not correspond to any existing payment method
class TransactionRepository:

    @deal.safe()
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
            created_at=token.created_at,  # TODO Ensure via type that datetime is timezone aware
            token=token.token,
            expires_at=token.expires_at,  # TODO Ensure via type that datetime is timezone aware
            fingerprint=token.fingerprint,
            metadata=token.metadata,
        )
        db_token.save()

        payment_method.tokens.append(db_token.to_domain())
        return payment_method
