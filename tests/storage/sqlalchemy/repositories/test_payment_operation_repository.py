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
def test_givenCorrectData_whenCallingRepositoryAdd_thenPaymentOperationGetsCreated(
    session: "orm.Session",
    sqlalchemy_assert_num_queries: Callable,
    operation_type: enums.OperationTypeEnum,
    operation_status: enums.OperationStatusEnum,
) -> None:

    # Given existing payment method row in payment methods table
    db_payment_attempt = factories.PaymentAttemptFactory()
    db_payment_method = factories.PaymentMethodFactory(payment_attempt_id=db_payment_attempt.id)
    payment_method = db_payment_method.to_domain()

    with sqlalchemy_assert_num_queries(5):
        result = storage.sqlalchemy.PaymentOperationRepository(session=session).add(
            payment_method=payment_method,
            type=operation_type,
            status=operation_status,
        )

    db_payment_operations = session.query(storage.sqlalchemy.models.PaymentOperation).all()
    assert len(db_payment_operations) == 1

    db_payment_operation = db_payment_operations[0]
    assert db_payment_operation.to_domain() == result

    assert len(payment_method.payment_operations) == 1
    assert payment_method.payment_operations[0] == result
