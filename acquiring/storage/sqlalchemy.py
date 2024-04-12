from dataclasses import dataclass
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import orm

from acquiring import domain, models

if TYPE_CHECKING:
    from acquiring import protocols


@dataclass
class PaymentMethodRepository:

    session: orm.Session

    def add(self, data: "protocols.DraftPaymentMethod") -> "protocols.PaymentMethod": ...  # type:ignore[empty-body]

    def get(self, id: UUID) -> "protocols.PaymentMethod":
        try:
            payment_method = self.session.query(models.PaymentMethod).filter_by(id=id).one()
            return payment_method.to_domain()
        except orm.exc.NoResultFound:
            raise domain.PaymentAttempt.DoesNotExist
