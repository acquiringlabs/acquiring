import functools
import uuid
from typing import Callable, Sequence

import pytest
from faker import Faker

from acquiring.utils import is_django_installed
from tests.storage.utils import skip_if_django_not_installed

fake = Faker()

if is_django_installed():
    import django
    from acquiring import domain, protocols, storage
    from tests.storage.django.factories import PaymentAttemptFactory, PaymentMethodFactory

    @pytest.fixture()
    def FakeModel() -> type[django.db.models.Model]:
        """
        Implements a model specifically to test more complex relations in the database, beyond defaults
        """

        class Klass(django.db.models.Model):
            name = django.db.models.CharField(max_length=100)
            payment_method = django.db.models.ForeignKey(
                storage.django.models.PaymentMethod,
                on_delete=django.db.models.CASCADE,
            )

            class Meta:
                app_label = "acquiring"

        return Klass


def with_fake_model(function: Callable) -> Callable:
    """
    Introduces a Fake Model into the database schema and removes it after the test is complete.

    This wrapper assumes that the database is SQLite. If needed, it can be split into two decorators
    (one for the schema_editor, another for he PRAGMA execution) to accommodate other database engines.
    """

    @functools.wraps(function)
    def wrapper(
        transactional_db: type,
        django_db_blocker: type,
        FakeModel: "type[django.db.models.Model]",
        *args: Sequence,
        **kwargs: dict,
    ) -> None:
        if not is_django_installed():
            return function(transactional_db, django_db_blocker, FakeModel, *args, **kwargs)

        # https://pytest-django.readthedocs.io/en/latest/database.html#django-db-blocker
        with django_db_blocker.unblock():  # type:ignore[attr-defined]

            cursor = django.db.connection.cursor()
            cursor.execute("PRAGMA foreign_keys = OFF")

            with django.db.connection.schema_editor() as schema_editor:
                schema_editor.create_model(FakeModel)

            result = function(transactional_db, django_db_blocker, FakeModel, *args, **kwargs)

            with django.db.connection.schema_editor() as schema_editor:
                schema_editor.delete_model(FakeModel)

            cursor.execute("PRAGMA foreign_keys = ON")

            return result

    return wrapper


@skip_if_django_not_installed
@with_fake_model
def test_givenAMoreComplexData_whenFakeRepositoryAddUnderUnitOfWork_thenComplexDataCommits(
    transactional_db: type,
    django_db_blocker: type,
    FakeModel: "type[django.db.models.Model]",
    django_assert_num_queries: Callable,
) -> None:
    """This test should not be wrapped inside mark.django_db"""

    class TemporaryRepository:

        def add(self, data: "protocols.DraftPaymentMethod") -> "protocols.PaymentMethod":
            db_payment_method = storage.django.models.PaymentMethod(
                payment_attempt_id=data.payment_attempt.id,
                confirmable=data.confirmable,
            )
            db_payment_method.save()

            db_extra = FakeModel(name="test", payment_method=db_payment_method)
            db_extra.save()
            return db_payment_method.to_domain()

        def get(self, id: uuid.UUID) -> "protocols.PaymentMethod":
            return PaymentMethodFactory(payment_attempt=PaymentAttemptFactory()).to_domain()

    payment_attempt = PaymentAttemptFactory().to_domain()

    with django_assert_num_queries(8):
        with storage.django.DjangoUnitOfWork():
            TemporaryRepository().add(
                domain.DraftPaymentMethod(
                    payment_attempt=payment_attempt,
                    confirmable=False,
                )
            )

    assert storage.django.models.PaymentMethod.objects.count() == 1
    db_payment_method = storage.django.models.PaymentMethod.objects.get()

    assert FakeModel.objects.filter(payment_method=db_payment_method).count() == 1


@skip_if_django_not_installed
@with_fake_model
def test_givenAMoreComplexData_whenFakeRepositoryAddFailsUnderUnitOfWork_thenComplexDataRollsBack(
    transactional_db: type,
    django_db_blocker: type,
    FakeModel: "type[django.db.models.Model]",
    django_assert_num_queries: Callable,
) -> None:
    """This test should not be wrapped inside mark.django_db"""

    class TestException(Exception):
        pass

    class TemporaryRepository:

        def add(self, data: "protocols.DraftPaymentMethod") -> "protocols.PaymentMethod":
            db_payment_method = storage.django.models.PaymentMethod(
                payment_attempt_id=data.payment_attempt.id,
                confirmable=data.confirmable,
            )
            db_payment_method.save()

            db_extra = FakeModel(name="test", payment_method=db_payment_method)
            db_extra.save()
            raise TestException

        def get(self, id: uuid.UUID) -> "protocols.PaymentMethod":
            return PaymentMethodFactory(payment_attempt=PaymentAttemptFactory()).to_domain()

    payment_attempt = PaymentAttemptFactory().to_domain()

    with django_assert_num_queries(4), pytest.raises(TestException):
        with storage.django.DjangoUnitOfWork():
            TemporaryRepository().add(
                domain.DraftPaymentMethod(
                    payment_attempt=payment_attempt,
                    confirmable=False,
                )
            )

    assert storage.django.models.PaymentMethod.objects.count() == 0
    assert FakeModel.objects.count() == 0


@skip_if_django_not_installed
@with_fake_model
def test_givenAMoreComplexData_whenTwoFakeRepositoriesAddUnderUnitOfWorkWithCommitInbetween_thenComplexDataCommits(
    transactional_db: type,
    django_db_blocker: type,
    FakeModel: "type[django.db.models.Model]",
    django_assert_num_queries: Callable,
) -> None:
    """This test should not be wrapped inside mark.django_db"""

    class TemporaryPaymentMethodRepository:

        def add(self, data: "protocols.DraftPaymentMethod") -> "protocols.PaymentMethod":
            db_payment_method = storage.django.models.PaymentMethod(
                payment_attempt_id=data.payment_attempt.id,
                confirmable=data.confirmable,
            )
            db_payment_method.save()
            return db_payment_method.to_domain()

        def get(self, id: uuid.UUID) -> "protocols.PaymentMethod":
            return PaymentMethodFactory(payment_attempt=PaymentAttemptFactory()).to_domain()

    class TestException(Exception):
        pass

    class TemporaryFakeModelRepository:

        def add(self) -> "protocols.PaymentMethod":
            raise TestException

        def get(self, id: uuid.UUID) -> "protocols.PaymentMethod":
            return PaymentMethodFactory(payment_attempt=PaymentAttemptFactory()).to_domain()

    payment_attempt = PaymentAttemptFactory().to_domain()

    with django_assert_num_queries(9), pytest.raises(TestException):
        with storage.django.DjangoUnitOfWork() as uow:
            TemporaryPaymentMethodRepository().add(
                domain.DraftPaymentMethod(
                    payment_attempt=payment_attempt,
                    confirmable=False,
                )
            )
            uow.commit()
            TemporaryFakeModelRepository().add()

    assert storage.django.models.PaymentMethod.objects.count() == 1


@skip_if_django_not_installed
@with_fake_model
def test_givenAMoreComplexData_whenTwoFakeRepositoriesAddUnderUnitOfWorkWithRollbackInbetween_thenComplexDataRollsback(
    transactional_db: type,
    django_db_blocker: type,
    FakeModel: "type[django.db.models.Model]",
    django_assert_num_queries: Callable,
) -> None:
    """This test should not be wrapped inside mark.django_db"""

    class TemporaryPaymentMethodRepository:

        def add(self, data: "protocols.DraftPaymentMethod") -> "protocols.PaymentMethod":
            db_payment_method = storage.django.models.PaymentMethod(
                payment_attempt_id=data.payment_attempt.id,
                confirmable=data.confirmable,
            )
            db_payment_method.save()
            return db_payment_method.to_domain()

        def get(self, id: uuid.UUID) -> "protocols.PaymentMethod":
            return PaymentMethodFactory(payment_attempt=PaymentAttemptFactory()).to_domain()

    class TemporaryFakeModelRepository:

        def add(self) -> None:
            pass

        def get(self, id: uuid.UUID) -> "protocols.PaymentMethod":
            return PaymentMethodFactory(payment_attempt=PaymentAttemptFactory()).to_domain()

    payment_attempt = PaymentAttemptFactory().to_domain()

    with django_assert_num_queries(7):
        with storage.django.DjangoUnitOfWork() as uow:
            TemporaryPaymentMethodRepository().add(
                domain.DraftPaymentMethod(
                    payment_attempt=payment_attempt,
                    confirmable=False,
                )
            )
            uow.rollback()
            TemporaryFakeModelRepository().add()

    assert storage.django.models.PaymentMethod.objects.count() == 0
