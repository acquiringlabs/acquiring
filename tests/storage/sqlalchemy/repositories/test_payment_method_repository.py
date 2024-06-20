from typing import Callable

import pytest
from faker import Faker

from acquiring import domain, storage, utils
from tests.storage.utils import skip_if_sqlalchemy_not_installed

fake = Faker()

if utils.is_sqlalchemy_installed():
    from sqlalchemy import orm

    from tests.storage.sqlalchemy import factories


@skip_if_sqlalchemy_not_installed
def test_givenExistingPaymentMethodRow_whenCallingRepositoryGet_thenPaymentMethodGetsRetrieved(
    session: "orm.Session",
    sqlalchemy_assert_num_queries: Callable,
) -> None:
    payment_attempt = factories.PaymentAttemptFactory()
    payment_method = factories.PaymentMethodFactory(payment_attempt_id=payment_attempt.id)

    with sqlalchemy_assert_num_queries(5):
        result = storage.sqlalchemy.PaymentMethodRepository(
            session=session,
        ).get(id=payment_method.id)

    assert result.payment_attempt_id == payment_attempt.id
    assert result == payment_method.to_domain()


@skip_if_sqlalchemy_not_installed
def test_givenNonExistingPaymentMethodRow_whenCallingRepositoryGet_thenDoesNotExistGetsRaise(
    session: "orm.Session",
    sqlalchemy_assert_num_queries: Callable,
) -> None:
    from tests.domain import factories as domain_factories

    payment_method = domain_factories.PaymentMethodFactory(
        payment_attempt_id=domain_factories.PaymentAttemptFactory().id,
    )

    with sqlalchemy_assert_num_queries(5), pytest.raises(domain.PaymentMethod.DoesNotExist):
        storage.sqlalchemy.PaymentMethodRepository(
            session=session,
        ).get(id=payment_method.id)


@skip_if_sqlalchemy_not_installed
@pytest.mark.django_db
def test_givenCorrectData_whenCallingRepositoryAdd_thenPaymentMethodGetsCreated(
    session: "orm.Session",
    sqlalchemy_assert_num_queries: Callable,
) -> None:

    payment_attempt = factories.PaymentAttemptFactory()
    data = domain.DraftPaymentMethod(
        payment_attempt_id=payment_attempt.id,
    )

    with sqlalchemy_assert_num_queries(7):
        result = storage.sqlalchemy.PaymentMethodRepository(session=session).add(data)
        session.commit()

    db_payment_methods = session.query(storage.sqlalchemy.models.PaymentMethod).all()
    assert len(db_payment_methods) == 1
    db_payment_method = db_payment_methods[0]

    assert db_payment_method.id == result.id
    assert db_payment_method.payment_attempt_id == payment_attempt.id
    assert db_payment_method.operation_events == []
