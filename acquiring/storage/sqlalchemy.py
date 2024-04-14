from dataclasses import dataclass
from typing import TYPE_CHECKING
from uuid import UUID

import deal
from sqlalchemy import orm

from acquiring import domain, models

if TYPE_CHECKING:
    from acquiring import protocols


@dataclass
class PaymentMethodRepository:

    session: orm.Session

    def add(self, data: "protocols.DraftPaymentMethod") -> "protocols.PaymentMethod": ...  # type:ignore[empty-body]

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
