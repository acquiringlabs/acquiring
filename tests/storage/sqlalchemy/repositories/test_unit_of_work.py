import uuid
from dataclasses import dataclass
from typing import Any, Callable, Generator

import pytest
from faker import Faker

from acquiring.utils import is_sqlalchemy_installed
from tests.storage.utils import skip_if_sqlalchemy_not_installed

fake = Faker()

if is_sqlalchemy_installed():
    import sqlalchemy
    from sqlalchemy import orm

    from acquiring import domain, protocols, storage
    from tests.storage.sqlalchemy import factories

    # TODO Refactor typing for SQLAlchemy v2.1
    # See https://docs.sqlalchemy.org/en/20/orm/extensions/mypy.html
    @pytest.fixture()
    def FakeModel() -> Any:  # type:ignore[misc]
        """
        Implements a model specifically to test more complex relations in the database, beyond defaults
        """

        class Klass(storage.sqlalchemy.models.Model):
            __tablename__ = "fake_models"

            id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)

            name = sqlalchemy.Column(sqlalchemy.String(30))
            payment_method_id = sqlalchemy.Column(
                sqlalchemy.String, sqlalchemy.ForeignKey("acquiring_paymentmethods.id"), nullable=False
            )

        return Klass

    @pytest.fixture
    def db_with_fake_model(FakeModel: Any, session: "orm.Session") -> Generator:  # type:ignore[misc]
        """
        Introduces a Fake Model into the database schema and removes it after the test is complete.

        This wrapper assumes that the database is SQLite. If needed, it can be split into two decorators
        (one for the schema_editor, another for he PRAGMA execution) to accommodate other database engines.
        """

        if not is_sqlalchemy_installed():
            yield

        connection = session.connection()

        connection.execute("PRAGMA foreign_keys = OFF")
        FakeModel.__table__.create(connection)

        try:
            yield
        finally:
            FakeModel.__table__.drop(connection)

            # Clear, then load all available table definitions from the database
            # See https://docs.sqlalchemy.org/en/14/core/metadata.html#sqlalchemy.schema.MetaData.reflect
            metadata = storage.sqlalchemy.models.Model.metadata
            metadata.clear()
            metadata.reflect(bind=connection)
            connection.execute("PRAGMA foreign_keys = ON")


@skip_if_sqlalchemy_not_installed
def test_givenAMoreComplexData_whenFakeRepositoryAddUnderUnitOfWork_thenComplexDataCommits(  # type:ignore[misc]
    db_with_fake_model: Generator,
    session: "orm.Session",
    sqlalchemy_assert_num_queries: Callable,
    FakeModel: Any,
) -> None:
    """This test should not be wrapped inside mark.django_db"""

    @dataclass
    class TemporaryRepository:
        session: orm.Session

        def add(self, data: "protocols.DraftPaymentMethod") -> "protocols.PaymentMethod":
            db_payment_method = storage.sqlalchemy.models.PaymentMethod(
                payment_attempt_id=data.payment_attempt.id,
                confirmable=data.confirmable,
            )
            self.session.add(db_payment_method)
            self.session.flush()

            db_extra = FakeModel(name="test", payment_method_id=db_payment_method.id)
            self.session.add(db_extra)
            return db_payment_method.to_domain()

        def get(self, id: uuid.UUID) -> "protocols.PaymentMethod":
            return factories.PaymentMethodFactory(payment_attempt=factories.PaymentAttemptFactory()).to_domain()

    payment_attempt = factories.PaymentAttemptFactory().to_domain()

    with sqlalchemy_assert_num_queries(5):
        with storage.sqlalchemy.SqlAlchemyUnitOfWork(
            payment_method_repository_class=TemporaryRepository,
            payment_operation_repository_class=TemporaryRepository,
            block_event_repository_class=TemporaryRepository,
        ) as uow:
            uow.payment_methods.add(
                domain.DraftPaymentMethod(
                    payment_attempt=payment_attempt,
                    confirmable=False,
                )
            )
            uow.commit()

    assert session.query(sqlalchemy.func.count(storage.sqlalchemy.models.PaymentMethod.id)).scalar() == 1
    db_payment_method = session.query(storage.sqlalchemy.models.PaymentMethod).first()

    assert (
        session.query(sqlalchemy.func.count()).filter(FakeModel.payment_method_id == db_payment_method.id).scalar() == 1
    )


@skip_if_sqlalchemy_not_installed
def test_givenAMoreComplexData_whenFakeRepositoryAddFailsUnderUnitOfWork_thenComplexDataRollsBack(  # type:ignore[misc]
    db_with_fake_model: Generator,
    session: "orm.Session",
    sqlalchemy_assert_num_queries: Callable,
    FakeModel: Any,
) -> None:

    class TestException(Exception):
        pass

    @dataclass
    class TemporaryRepository:
        session: orm.Session

        def add(self, data: "protocols.DraftPaymentMethod") -> "protocols.PaymentMethod":
            db_payment_method = storage.sqlalchemy.models.PaymentMethod(
                payment_attempt_id=data.payment_attempt.id,
                confirmable=data.confirmable,
            )
            self.session.add(db_payment_method)
            self.session.flush()

            db_extra = FakeModel(name="test", payment_method_id=db_payment_method.id)
            self.session.add(db_extra)
            raise TestException

        def get(self, id: uuid.UUID) -> "protocols.PaymentMethod":
            return factories.PaymentMethodFactory(payment_attempt=factories.PaymentAttemptFactory()).to_domain()

    payment_attempt = factories.PaymentAttemptFactory().to_domain()

    with sqlalchemy_assert_num_queries(5), pytest.raises(TestException):
        with storage.sqlalchemy.SqlAlchemyUnitOfWork(
            payment_method_repository_class=TemporaryRepository,
            payment_operation_repository_class=TemporaryRepository,
            block_event_repository_class=TemporaryRepository,
        ) as uow:
            uow.payment_methods.add(
                domain.DraftPaymentMethod(
                    payment_attempt=payment_attempt,
                    confirmable=False,
                )
            )

    assert session.query(sqlalchemy.func.count(storage.sqlalchemy.models.PaymentMethod.id)).scalar() == 0
    assert session.query(sqlalchemy.func.count(FakeModel.id)).scalar() == 0


@skip_if_sqlalchemy_not_installed
def test_givenAMoreComplexData_whenTwoFakeRepositoriesAddUnderUnitOfWorkWithCommitInbetween_thenComplexDataCommits(  # type:ignore[misc]
    db_with_fake_model: Generator,
    session: "orm.Session",
    sqlalchemy_assert_num_queries: Callable,
    FakeModel: Any,
) -> None:

    class TestException(Exception):
        pass

    @dataclass
    class TemporaryRepository:
        session: orm.Session

        def add(self, data: "protocols.DraftPaymentMethod") -> "protocols.PaymentMethod":
            db_payment_method = storage.sqlalchemy.models.PaymentMethod(
                payment_attempt_id=data.payment_attempt.id,
                confirmable=data.confirmable,
            )
            self.session.add(db_payment_method)
            self.session.flush()

            db_extra = FakeModel(name="test", payment_method_id=db_payment_method.id)
            self.session.add(db_extra)
            return db_payment_method.to_domain()

        def get(self, id: uuid.UUID) -> "protocols.PaymentMethod":
            return factories.PaymentMethodFactory(payment_attempt=factories.PaymentAttemptFactory()).to_domain()

    @dataclass
    class FakeModelRepository:
        session: orm.Session

        def add(self) -> "protocols.PaymentMethod":
            raise TestException

        def get(self, id: uuid.UUID) -> "protocols.PaymentMethod":
            return factories.PaymentMethodFactory(payment_attempt=factories.PaymentAttemptFactory()).to_domain()

    payment_attempt = factories.PaymentAttemptFactory().to_domain()
    with sqlalchemy_assert_num_queries(5), pytest.raises(TestException):
        with storage.sqlalchemy.SqlAlchemyUnitOfWork(
            payment_method_repository_class=TemporaryRepository,
            payment_operation_repository_class=TemporaryRepository,
            block_event_repository_class=TemporaryRepository,
        ) as uow:
            uow.payment_methods.add(
                domain.DraftPaymentMethod(
                    payment_attempt=payment_attempt,
                    confirmable=False,
                )
            )
            uow.commit()
            FakeModelRepository(uow.session).add()

    assert session.query(sqlalchemy.func.count(storage.sqlalchemy.models.PaymentMethod.id)).scalar() == 1


@skip_if_sqlalchemy_not_installed
def test_givenAMoreComplexData_whenTwoFakeRepositoriesAddUnderUnitOfWorkWithRollbackInbetween_thenComplexDataRollsback(  # type:ignore[misc]
    db_with_fake_model: Generator,
    session: "orm.Session",
    sqlalchemy_assert_num_queries: Callable,
    FakeModel: Any,
) -> None:
    @dataclass
    class TemporaryRepository:
        session: orm.Session

        def add(self, data: "protocols.DraftPaymentMethod") -> "protocols.PaymentMethod":
            db_payment_method = storage.sqlalchemy.models.PaymentMethod(
                payment_attempt_id=data.payment_attempt.id,
                confirmable=data.confirmable,
            )
            self.session.add(db_payment_method)
            self.session.flush()

            db_extra = FakeModel(name="test", payment_method_id=db_payment_method.id)
            self.session.add(db_extra)
            return db_payment_method.to_domain()

        def get(self, id: uuid.UUID) -> "protocols.PaymentMethod":
            return factories.PaymentMethodFactory(payment_attempt=factories.PaymentAttemptFactory()).to_domain()

    @dataclass
    class FakeModelRepository:
        session: orm.Session

        def add(self) -> None:
            pass

        def get(self, id: uuid.UUID) -> "protocols.PaymentMethod":
            return factories.PaymentMethodFactory(payment_attempt=factories.PaymentAttemptFactory()).to_domain()

    payment_attempt = factories.PaymentAttemptFactory().to_domain()
    with sqlalchemy_assert_num_queries(5):
        with storage.sqlalchemy.SqlAlchemyUnitOfWork(
            payment_method_repository_class=TemporaryRepository,
            payment_operation_repository_class=TemporaryRepository,
            block_event_repository_class=TemporaryRepository,
        ) as uow:
            uow.payment_methods.add(
                domain.DraftPaymentMethod(
                    payment_attempt=payment_attempt,
                    confirmable=False,
                )
            )
            uow.rollback()
            FakeModelRepository(uow.session).add()

    assert session.query(sqlalchemy.func.count(storage.sqlalchemy.models.PaymentMethod.id)).scalar() == 0
