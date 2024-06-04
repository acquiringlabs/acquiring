import uuid
from datetime import datetime
from typing import Callable

import pytest
from faker import Faker

from acquiring import utils
from acquiring.enums import OperationStatusEnum
from tests.storage.utils import skip_if_sqlalchemy_not_installed

if utils.is_sqlalchemy_installed():
    from sqlalchemy import orm

    from acquiring import domain, storage
    from tests.storage.sqlalchemy import factories

fake = Faker()


@skip_if_sqlalchemy_not_installed
@pytest.mark.parametrize("status", OperationStatusEnum)
def test_givenCorrectData_whenCallingRepositoryAdd_thenBlockEventGetsCreated(
    session: "orm.Session",
    sqlalchemy_assert_num_queries: Callable,
    status: OperationStatusEnum,
) -> None:

    db_payment_method = factories.PaymentMethodFactory(payment_attempt=factories.PaymentAttemptFactory())
    block_event = domain.BlockEvent(
        created_at=datetime.now(),
        status=status,
        payment_method_id=db_payment_method.id,
        block_name="test",
    )

    with sqlalchemy_assert_num_queries(5):
        storage.sqlalchemy.BlockEventRepository(
            session=session,
        ).add(db_payment_method.to_domain(), block_event)
        session.commit()

    db_block_events = session.query(storage.sqlalchemy.models.BlockEvent).all()
    assert len(db_block_events) == 1
    db_block_event = db_block_events[0]

    assert db_block_event.status == block_event.status
    assert db_block_event.payment_method_id == block_event.payment_method_id
    assert db_block_event.block_name == block_event.block_name


@skip_if_sqlalchemy_not_installed
@pytest.mark.parametrize("status", OperationStatusEnum)
def test_givenAllData_whenCallingRepositoryAdd_thenBlockEventGetsCreated(
    status: OperationStatusEnum,
    sqlalchemy_assert_num_queries: Callable,
    session: "orm.Session",
) -> None:
    block_name = fake.name()

    db_payment_method = factories.PaymentMethodFactory(payment_attempt=factories.PaymentAttemptFactory())
    block_event = domain.BlockEvent(
        created_at=datetime.now(),
        status=status,
        payment_method_id=db_payment_method.id,
        block_name=block_name,
    )

    with sqlalchemy_assert_num_queries(5):
        storage.sqlalchemy.BlockEventRepository(
            session=session,
        ).add(db_payment_method.to_domain(), block_event)
        session.commit()

    db_block_event = (
        session.query(storage.sqlalchemy.models.BlockEvent)
        .filter_by(block_name=block_name, payment_method_id=db_payment_method.id, status=status)
        .one()
    )

    assert db_block_event.status == block_event.status
    assert db_block_event.payment_method_id == block_event.payment_method_id
    assert db_block_event.block_name == block_event.block_name


@skip_if_sqlalchemy_not_installed
def test_givenPaymentMethodWithDifferentIdThanTheOneStoredInBlockEvent_thenErrorGetsRaised(
    session: "orm.Session",
) -> None:
    block_name = fake.name()

    db_payment_method = factories.PaymentMethodFactory(payment_attempt=factories.PaymentAttemptFactory())
    block_event = domain.BlockEvent(
        created_at=datetime.now(),
        status=OperationStatusEnum.PENDING,
        payment_method_id=uuid.uuid4(),
        block_name=block_name,
    )

    with pytest.raises(ValueError):
        storage.sqlalchemy.BlockEventRepository(
            session=session,
        ).add(db_payment_method.to_domain(), block_event)
