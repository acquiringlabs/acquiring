from dataclasses import dataclass
from uuid import UUID

import deal
from sqlalchemy import orm

from acquiring import domain, enums, protocols

from . import models


@dataclass
class PaymentMethodRepository:

    session: orm.Session

    @deal.safe()
    def add(self, data: "protocols.DraftPaymentMethod") -> "protocols.PaymentMethod":
        db_payment_method = models.PaymentMethod(
            payment_attempt_id=data.payment_attempt.id,
            confirmable=data.confirmable,
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
class PaymentOperationRepository:

    session: orm.Session

    @deal.safe()
    def add(
        self,
        payment_method: "protocols.PaymentMethod",
        type: enums.OperationTypeEnum,
        status: enums.OperationStatusEnum,
    ) -> "protocols.PaymentOperation":
        db_payment_operation = models.PaymentOperation(
            payment_method_id=payment_method.id,
            type=type,
            status=status,
        )
        self.session.add(db_payment_operation)
        self.session.flush()
        payment_operation = db_payment_operation.to_domain()
        payment_method.payment_operations.append(payment_operation)
        return payment_operation

    def get(self, id: UUID) -> "protocols.PaymentOperation": ...  # type: ignore[empty-body]


@dataclass
class BlockEventRepository:

    session: orm.Session

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
