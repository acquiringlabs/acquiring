from dataclasses import dataclass, field
from types import TracebackType
from typing import Optional, Self

from sqlalchemy import orm


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
