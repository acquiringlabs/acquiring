from dataclasses import dataclass
from uuid import UUID

import deal
from sqlalchemy import orm

from acquiring import domain, enums, protocols

from . import models


@dataclass
class PaymentAttemptRepository:

    session: orm.Session

    def add(self, data: "protocols.DraftPaymentAttempt") -> "protocols.PaymentAttempt": ...  # type:ignore[empty-body]

    @deal.reason(
        domain.PaymentAttempt.DoesNotExist,
        lambda self, id: self.session.query(models.PaymentAttempt).filter_by(id=id).count() == 0,
    )
    def get(self, id: UUID) -> "protocols.PaymentAttempt":
        try:
            return (
                self.session.query(models.PaymentAttempt)
                .outerjoin(models.PaymentMethod, models.PaymentMethod.payment_attempt_id == models.PaymentAttempt.id)
                .filter(models.PaymentAttempt.id == id)
                .one()
                .to_domain()
            )
        except orm.exc.NoResultFound:
            raise domain.PaymentAttempt.DoesNotExist


@dataclass
class MilestoneRepository:

    session: orm.Session

    @deal.safe
    def add(
        self,
        payment_method: "protocols.PaymentMethod",
        type: enums.AtemptStatusEnum,
    ) -> "protocols.Milestone":
        db_milestone = models.Milestone(
            payment_method_id=payment_method.id,
            payment_attempt_id=payment_method.payment_attempt_id,
            type=type,
        )
        self.session.add(db_milestone)
        self.session.flush()
        return db_milestone.to_domain()

    def get(self, id: UUID) -> "protocols.Milestone": ...  # type:ignore[empty-body]


@dataclass
class PaymentMethodRepository:

    session: orm.Session

    @deal.safe
    def add(self, data: "protocols.DraftPaymentMethod") -> "protocols.PaymentMethod":
        db_payment_method = models.PaymentMethod(
            payment_attempt_id=data.payment_attempt_id,
        )
        self.session.add(db_payment_method)
        self.session.flush()
        return db_payment_method.to_domain()

    @deal.reason(
        domain.PaymentMethod.DoesNotExist,
        lambda self, id: self.session.query(models.PaymentMethod).filter_by(id=id).count() == 0,
    )
    def get(self, id: UUID) -> "protocols.PaymentMethod":
        try:
            return (
                self.session.query(models.PaymentMethod)
                .options(
                    orm.joinedload("payment_attempt"),
                )
                .filter_by(id=id)
                .one()
                .to_domain()
            )
        except orm.exc.NoResultFound:
            raise domain.PaymentMethod.DoesNotExist


@dataclass
class OperationEventRepository:

    session: orm.Session

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
        self.session.add(db_operation_event)
        self.session.flush()
        operation_event = db_operation_event.to_domain()
        payment_method.operation_events.append(operation_event)
        return operation_event

    def get(self, id: UUID) -> "protocols.OperationEvent": ...  # type: ignore[empty-body]


@dataclass
class BlockEventRepository:

    session: orm.Session

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
        self.session.add(db_block_event)
        return db_block_event.to_domain()

    def get(self, id: UUID) -> "protocols.BlockEvent": ...  # type: ignore[empty-body]


@dataclass
class TransactionRepository:

    session: orm.Session

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
        self.session.add(db_transaction)
        return db_transaction.to_domain()

    def get(self, id: UUID) -> "protocols.BlockEvent": ...  # type: ignore[empty-body]
