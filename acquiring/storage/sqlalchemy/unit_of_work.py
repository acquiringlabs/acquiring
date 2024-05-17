import os
from dataclasses import dataclass, field
from types import TracebackType
from typing import Optional, Self

import sqlalchemy
from sqlalchemy import orm

from acquiring import protocols


@dataclass
class SqlAlchemyUnitOfWork:
    """
    Unit of Work context manager for SQLAlchemy database engine.

    See Unit of Work pattern here: https://martinfowler.com/eaaCatalog/unitOfWork.html
    """

    payment_method_repository_class: type[protocols.Repository]
    payment_methods: protocols.Repository = field(init=False)

    payment_operation_repository_class: type[protocols.Repository]
    payment_operations: protocols.Repository = field(init=False)

    block_event_repository_class: type[protocols.Repository]
    block_events: protocols.Repository = field(init=False)

    transaction_repository_class: type[protocols.Repository]
    transactions: protocols.Repository = field(init=False)

    session_factory: orm.sessionmaker = orm.sessionmaker(
        bind=sqlalchemy.create_engine(os.environ.get("SQLALCHEMY_DATABASE_URL"))
    )
    session: orm.Session = field(init=False)

    def __enter__(self) -> Self:
        self.session = self.session_factory()

        self.payment_methods = self.payment_method_repository_class(session=self.session)  # type: ignore[call-arg]
        self.payment_operations = self.payment_operation_repository_class(session=self.session)  # type: ignore[call-arg]
        self.block_events = self.block_event_repository_class(session=self.session)  # type: ignore[call-arg]
        self.transactions = self.transaction_repository_class(session=self.session)  # type: ignore[call-arg]

        return self

    def __exit__(
        self,
        exc_type: Optional[type[BaseException]],
        exc_value: Optional[type[BaseException]],
        exc_tb: Optional[TracebackType],
    ) -> None:
        # Autocommit disasbled, see PEP 249 - Python Database API Specification v2.0
        if exc_type is not None:
            self.rollback()
        self.session.close()

    def commit(self) -> None:
        self.session.commit()

    def rollback(self) -> None:
        self.session.rollback()
