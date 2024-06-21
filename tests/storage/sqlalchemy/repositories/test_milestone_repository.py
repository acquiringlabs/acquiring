from typing import Callable

import pytest
from faker import Faker

from acquiring import enums
from acquiring.utils import is_sqlalchemy_installed
from tests.storage.utils import skip_if_sqlalchemy_not_installed

if is_sqlalchemy_installed():
    from sqlalchemy import orm

    from acquiring import storage
    from tests.storage.sqlalchemy import factories

fake = Faker()


@skip_if_sqlalchemy_not_installed
@pytest.mark.django_db
@pytest.mark.parametrize("type", enums.AtemptStatusEnum)
def test_givenCorrectData_whenCallingRepositoryAdd_thenMilestoneGetsCreated(
    session: "orm.Session",
    sqlalchemy_assert_num_queries: Callable,
    type: enums.AtemptStatusEnum,
) -> None:

    db_payment_method = factories.PaymentMethodFactory(payment_attempt_id=factories.PaymentAttemptFactory().id)

    with sqlalchemy_assert_num_queries(5):
        storage.sqlalchemy.MilestoneRepository(session).add(db_payment_method.to_domain(), type)
        session.commit()

    db_milestones = session.query(storage.sqlalchemy.models.Milestone).all()
    assert len(db_milestones) == 1
    db_milestone = db_milestones[0]

    assert db_milestone.payment_method_id == db_payment_method.id
    assert db_milestone.payment_attempt_id == db_payment_method.payment_attempt.id
    assert db_milestone.type == type
