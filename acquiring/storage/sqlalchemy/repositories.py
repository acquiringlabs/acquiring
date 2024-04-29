from dataclasses import dataclass
from uuid import UUID

import deal
from sqlalchemy import orm

from acquiring import domain, protocols
from . import models


@dataclass
class PaymentMethodRepository:

    @deal.safe()
    def add(self, session: orm.Session, data: "protocols.DraftPaymentMethod") -> "protocols.PaymentMethod":
        db_payment_method = models.PaymentMethod(
            payment_attempt_id=data.payment_attempt.id,
            confirmable=data.confirmable,
        )
        session.add(db_payment_method)
        session.flush()
        return db_payment_method.to_domain()

    @deal.reason(
        domain.PaymentMethod.DoesNotExist,
        lambda self, session, id: session.query(models.PaymentMethod).filter_by(id=id).count() == 0,
    )
    def get(self, session: orm.Session, id: UUID) -> "protocols.PaymentMethod":
        try:
            return (
                session.query(models.PaymentMethod)
                .options(
                    orm.joinedload("payment_attempt"),
                )
                .filter_by(id=id)
                .one()
                .to_domain()
            )
        except orm.exc.NoResultFound:
            raise domain.PaymentMethod.DoesNotExist
