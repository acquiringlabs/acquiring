from dataclasses import dataclass, field
from types import TracebackType
from typing import TYPE_CHECKING, Optional, Self
from uuid import UUID

import deal
from sqlalchemy import orm

from acquiring import domain, models

if TYPE_CHECKING:
    from acquiring import protocols


@dataclass
class SqlAlchemyUnitOfWork:
    session_factory: orm.sessionmaker
    session: orm.Session = field(init=False)

    def __enter__(self) -> Self:
        self.session = self.session_factory()
        return self

    def __exit__(
        self,
        exc_type: Optional[type[BaseException]],
        exc_value: Optional[type[BaseException]],
        exc_tb: Optional[TracebackType],
    ) -> None:
        self.session.close()

    def commit(self) -> None:
        self.session.commit()

    def rollback(self) -> None:
        self.session.rollback()


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
        self.session.commit()
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
