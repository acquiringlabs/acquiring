import uuid
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

    with sqlalchemy_assert_num_queries(5):
        result = storage.sqlalchemy.PaymentAttemptRepository(
            session=session,
        ).get(id=payment_attempt.id)

    assert result == payment_attempt.to_domain()


@skip_if_sqlalchemy_not_installed
def test_givenNonExistingPaymentMethodRow_whenCallingRepositoryGet_thenDoesNotExistGetsRaise(
    session: "orm.Session",
    sqlalchemy_assert_num_queries: Callable,
) -> None:

    with sqlalchemy_assert_num_queries(5), pytest.raises(domain.PaymentAttempt.DoesNotExist):
        storage.sqlalchemy.PaymentAttemptRepository(
            session=session,
        ).get(id=str(uuid.uuid4()))
