from typing import TYPE_CHECKING
from uuid import UUID

import django.db.transaction

from django_acquiring import domain, models
from django_acquiring.enums import OperationStatusEnum, OperationTypeEnum

if TYPE_CHECKING:
    from django_acquiring import protocols


class PaymentAttemptRepository:
    def add(self, data: "protocols.AbstractDraftPaymentAttempt") -> "protocols.AbstractPaymentAttempt":
        payment_attempt = models.PaymentAttempt(
            order_id=data.order_id,
            amount=data.amount,
            currency=data.currency,
        )
        payment_attempt.save()
        return payment_attempt.to_domain()

    def get(self, id: UUID) -> "protocols.AbstractPaymentAttempt":
        try:
            payment_attempt = (
                models.PaymentAttempt.objects.prefetch_related("payment_methods", "payment_methods__payment_operations")
                .select_related("order")
                .get(id=id)
            )
            return payment_attempt.to_domain()
        except models.PaymentAttempt.DoesNotExist:
            raise domain.PaymentAttempt.DoesNotExist


class PaymentMethodRepository:
    def add(self, data: "protocols.AbstractDraftPaymentMethod") -> "protocols.AbstractPaymentMethod":
        with django.db.transaction.atomic():

            db_payment_method = models.PaymentMethod(
                payment_attempt_id=data.payment_attempt.id,
                confirmable=data.confirmable,
            )

            if data.token:
                db_token = models.Token(
                    payment_method=db_payment_method,
                    created_at=data.token.created_at,  # TODO Ensure via type that datetime is timezone aware
                    token=data.token.token,
                    expires_at=data.token.expires_at,  # TODO Ensure via type that datetime is timezone aware
                    fingerprint=data.token.fingerprint,
                    metadata=data.token.metadata,
                )
                db_token.save()
                db_payment_method.token = db_token
            db_payment_method.save()
        return db_payment_method.to_domain()

    def get(self, id: UUID) -> "protocols.AbstractPaymentMethod":
        try:
            payment_method = (
                models.PaymentMethod.objects.prefetch_related("payment_operations")
                .select_related("token", "payment_attempt")
                .get(id=id)
            )
            return payment_method.to_domain()
        except models.PaymentMethod.DoesNotExist:
            raise domain.PaymentMethod.DoesNotExist

    def add_token(
        self, payment_method: "protocols.AbstractPaymentMethod", token: "protocols.AbstractToken"
    ) -> "protocols.AbstractPaymentMethod":
        try:
            db_payment_method = models.PaymentMethod.objects.get(id=payment_method.id)
        except models.PaymentMethod.DoesNotExist:
            raise domain.PaymentMethod.DoesNotExist

        with django.db.transaction.atomic():
            db_token = models.Token(
                payment_method=db_payment_method,
                created_at=token.created_at,  # TODO Ensure via type that datetime is timezone aware
                token=token.token,
                expires_at=token.expires_at,  # TODO Ensure via type that datetime is timezone aware
                fingerprint=token.fingerprint,
                metadata=token.metadata,
            )
            db_token.save()
            db_payment_method.token = db_token
            db_payment_method.save()

            payment_method.token = db_token.to_domain()
            return payment_method


class PaymentOperationRepository:

    def add(
        self,
        payment_method: "protocols.AbstractPaymentMethod",
        type: OperationTypeEnum,
        status: OperationStatusEnum,
    ) -> "protocols.AbstractPaymentOperation":
        db_payment_operation = models.PaymentOperation(
            payment_method_id=payment_method.id,
            type=type,
            status=status,
        )
        db_payment_operation.save()
        payment_operation = db_payment_operation.to_domain()
        payment_method.payment_operations.append(payment_operation)
        return payment_operation

    def get(self, id: UUID) -> "protocols.AbstractPaymentOperation": ...  # type: ignore[empty-body]


# TODO Append block event to payment_method.block_events?
# TODO Test when payment method id does not correspond to any existing payment method
class BlockEventRepository:
    def add(self, block_event: "protocols.AbstractBlockEvent") -> "protocols.AbstractBlockEvent":
        db_block_event = models.BlockEvent(
            status=block_event.status,
            payment_method_id=block_event.payment_method_id,
            block_name=block_event.block_name,
        )
        db_block_event.save()
        return db_block_event.to_domain()

    def get(self, id: UUID) -> "protocols.AbstractBlockEvent": ...  # type: ignore[empty-body]


# TODO Append transaction to payment_method.transactions?
# TODO Test when payment method id does not correspond to any existing payment method
class TransactionRepository:
    def add(
        self,
        transaction: "protocols.AbstractTransaction",
    ) -> "protocols.AbstractTransaction":
        db_transaction = models.Transaction(
            created_at=transaction.created_at,
            external_id=transaction.external_id,
            payment_method_id=transaction.payment_method_id,
            provider_name=transaction.provider_name,
            raw_data=transaction.raw_data,
        )
        db_transaction.save()
        return db_transaction.to_domain()

    def get(self, id: UUID) -> "protocols.AbstractTransaction": ...  # type: ignore[empty-body]
