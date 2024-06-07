from datetime import datetime
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
@pytest.mark.django_db
def test_givenCorrectData_whenCallingRepositoryAdd_thenPaymentOperationGetsCreated(
    session: "orm.Session",
    sqlalchemy_assert_num_queries: Callable,
) -> None:
    db_payment_attempt = factories.PaymentAttemptFactory()
    db_payment_method = factories.PaymentMethodFactory(payment_attempt_id=db_payment_attempt.id)
    transaction = domain.Transaction(
        external_id=fake.uuid4(),
        timestamp=datetime.now(),
        provider_name=fake.company(),
        payment_method_id=db_payment_method.id,
        raw_data="",
    )

    with sqlalchemy_assert_num_queries(1):
        storage.sqlalchemy.TransactionRepository(session=session).add(
            transaction=transaction,
        )
        session.commit()

    db_transactions = session.query(storage.sqlalchemy.models.Transaction).all()
    assert len(db_transactions) == 1

    db_transaction = db_transactions[0]

    assert transaction == db_transaction.to_domain()
