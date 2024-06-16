from itertools import product
from typing import Callable

import pytest
from faker import Faker

from acquiring import enums, storage, utils
from tests.storage.utils import skip_if_sqlalchemy_not_installed

fake = Faker()

if utils.is_sqlalchemy_installed():
    from sqlalchemy import orm

    from tests.storage.sqlalchemy import factories


@skip_if_sqlalchemy_not_installed
@pytest.mark.django_db
@pytest.mark.parametrize(
    "operation_type, operation_status", product(enums.OperationTypeEnum, enums.OperationStatusEnum)
)
def test_givenCorrectData_whenCallingRepositoryAdd_thenOperationEventGetsCreated(
    session: "orm.Session",
    sqlalchemy_assert_num_queries: Callable,
    operation_type: enums.OperationTypeEnum,
    operation_status: enums.OperationStatusEnum,
) -> None:

    db_payment_attempt = factories.PaymentAttemptFactory()
    db_payment_method = factories.PaymentMethodFactory(payment_attempt_id=db_payment_attempt.id)
    payment_method = db_payment_method.to_domain()

    with sqlalchemy_assert_num_queries(5):
        result = storage.sqlalchemy.OperationEventRepository(session=session).add(
            payment_method=payment_method,
            type=operation_type,
            status=operation_status,
        )
        session.commit()

    db_operation_events = session.query(storage.sqlalchemy.models.OperationEvent).all()
    assert len(db_operation_events) == 1

    db_operation_event = db_operation_events[0]
    assert db_operation_event.type == operation_type
    assert db_operation_event.status == operation_status
    assert db_operation_event.payment_method_id == db_payment_method.id

    assert len(payment_method.operation_events) == 1
    assert payment_method.operation_events[0] == result
