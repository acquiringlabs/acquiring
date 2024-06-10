import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Callable, Optional

import pytest

from acquiring import domain, enums, protocols
from acquiring.domain.sagas import OperationResponse, refresh_payment_method
from tests import protocols as test_protocols
from tests.domain import factories


def test_givenAnExistingPM_whenCallingAMethodWrappedByRefreshPaymentMethodDecorator_thenPMGetsLatestData(
    fake_unit_of_work: type[test_protocols.FakeUnitOfWork],
    fake_payment_method_repository_class: Callable[
        [Optional[list[protocols.PaymentMethod]]],
        type[protocols.Repository],
    ],
    fake_payment_operation_repository_class: Callable[
        [Optional[set[protocols.PaymentOperation]]],
        type[test_protocols.FakeRepository],
    ],
    fake_block_event_repository_class: Callable[
        [Optional[set[protocols.BlockEvent]]],
        type[test_protocols.FakeRepository],
    ],
    fake_transaction_repository_class: Callable[
        [Optional[set[protocols.Transaction]]],
        type[test_protocols.FakeRepository],
    ],
) -> None:

    @dataclass
    class FakeSaga:
        unit_of_work: test_protocols.FakeUnitOfWork

        @refresh_payment_method
        def initialize(self, payment_method: "protocols.PaymentMethod") -> "protocols.OperationResponse":
            return OperationResponse(
                status=enums.OperationStatusEnum.COMPLETED,
                payment_method=payment_method,
                type=enums.OperationTypeEnum.INITIALIZE,
            )

    payment_method_id = uuid.uuid4()

    payment_method = domain.PaymentMethod(
        id=payment_method_id,
        payment_attempt=domain.PaymentAttempt(
            id=uuid.uuid4(),
            created_at=datetime.now(),
            amount=10,
            currency="USD",
            payment_method_ids=[payment_method_id],
        ),
        created_at=datetime.now(),
        confirmable=False,
        payment_operations=[
            factories.PaymentOperationFactory(
                created_at=datetime.now(),
                payment_method_id=payment_method_id,
                type=enums.OperationTypeEnum.INITIALIZE,
                status=enums.OperationStatusEnum.STARTED,
            ),
        ],
    )

    db_payment_method = domain.PaymentMethod(
        id=payment_method_id,
        payment_attempt=payment_method.payment_attempt,
        created_at=payment_method.created_at,
        confirmable=payment_method.confirmable,
        payment_operations=[
            factories.PaymentOperationFactory(
                created_at=datetime.now(),
                payment_method_id=payment_method_id,
                type=enums.OperationTypeEnum.INITIALIZE,
                status=enums.OperationStatusEnum.STARTED,
            ),
            factories.PaymentOperationFactory(
                created_at=datetime.now(),
                payment_method_id=payment_method_id,
                type=enums.OperationTypeEnum.INITIALIZE,
                status=enums.OperationStatusEnum.FAILED,
            ),
        ],
    )

    result = FakeSaga(
        unit_of_work=fake_unit_of_work(
            payment_method_repository_class=fake_payment_method_repository_class([db_payment_method]),
            payment_operation_repository_class=fake_payment_operation_repository_class(
                set(db_payment_method.payment_operations)
            ),
            block_event_repository_class=fake_block_event_repository_class(set()),
            transaction_repository_class=fake_transaction_repository_class(set()),
        )
    ).initialize(payment_method=payment_method)

    assert result.payment_method == db_payment_method


def test_givenANonExistingPM_whenCallingAMethodWrappedByRefreshPaymentMethodDecorator_thenMethodReturnsFailedResponse(
    fake_unit_of_work: type[test_protocols.FakeUnitOfWork],
    fake_payment_method_repository_class: Callable[
        [Optional[list[protocols.PaymentMethod]]],
        type[protocols.Repository],
    ],
    fake_payment_operation_repository_class: Callable[
        [Optional[set[protocols.PaymentOperation]]],
        type[test_protocols.FakeRepository],
    ],
    fake_block_event_repository_class: Callable[
        [Optional[set[protocols.BlockEvent]]],
        type[test_protocols.FakeRepository],
    ],
    fake_transaction_repository_class: Callable[
        [Optional[set[protocols.Transaction]]],
        type[test_protocols.FakeRepository],
    ],
) -> None:

    @dataclass
    class FakeSaga:
        unit_of_work: test_protocols.FakeUnitOfWork

        @refresh_payment_method
        def initialize(self, payment_method: "protocols.PaymentMethod") -> "protocols.OperationResponse":
            return OperationResponse(
                status=enums.OperationStatusEnum.COMPLETED,
                payment_method=payment_method,
                type=enums.OperationTypeEnum.INITIALIZE,
            )

    payment_method_id = uuid.uuid4()

    payment_method = domain.PaymentMethod(
        id=payment_method_id,
        payment_attempt=domain.PaymentAttempt(
            id=uuid.uuid4(),
            created_at=datetime.now(),
            amount=10,
            currency="USD",
            payment_method_ids=[payment_method_id],
        ),
        created_at=datetime.now(),
        confirmable=False,
        payment_operations=[
            factories.PaymentOperationFactory(
                created_at=datetime.now(),
                payment_method_id=payment_method_id,
                type=enums.OperationTypeEnum.INITIALIZE,
                status=enums.OperationStatusEnum.STARTED,
            ),
        ],
    )

    result = FakeSaga(
        unit_of_work=fake_unit_of_work(
            payment_method_repository_class=fake_payment_method_repository_class([]),
            payment_operation_repository_class=fake_payment_operation_repository_class(set()),
            block_event_repository_class=fake_block_event_repository_class(set()),
            transaction_repository_class=fake_transaction_repository_class(set()),
        )
    ).initialize(payment_method=payment_method)

    assert result.type == enums.OperationTypeEnum.INITIALIZE
    assert result.status == enums.OperationStatusEnum.FAILED
    assert result.error_message == "PaymentMethod not found"


def test_givenANonExistingPM_whenCallingAMethodWithInvalidNameWrappedByRefreshPaymentMethodDecorator_thenErrorGetsRaised(
    fake_unit_of_work: type[test_protocols.FakeUnitOfWork],
    fake_payment_method_repository_class: Callable[
        [Optional[list[protocols.PaymentMethod]]],
        type[protocols.Repository],
    ],
    fake_payment_operation_repository_class: Callable[
        [Optional[set[protocols.PaymentOperation]]],
        type[test_protocols.FakeRepository],
    ],
    fake_block_event_repository_class: Callable[
        [Optional[set[protocols.BlockEvent]]],
        type[test_protocols.FakeRepository],
    ],
    fake_transaction_repository_class: Callable[
        [Optional[set[protocols.Transaction]]],
        type[test_protocols.FakeRepository],
    ],
) -> None:

    @dataclass
    class FakeSaga:
        unit_of_work: test_protocols.FakeUnitOfWork

        @refresh_payment_method
        def do_something(self, payment_method: "protocols.PaymentMethod") -> "protocols.OperationResponse":
            return OperationResponse(
                status=enums.OperationStatusEnum.COMPLETED,
                payment_method=payment_method,
                type=enums.OperationTypeEnum.INITIALIZE,
            )

    payment_method_id = uuid.uuid4()

    payment_method = domain.PaymentMethod(
        id=payment_method_id,
        payment_attempt=domain.PaymentAttempt(
            id=uuid.uuid4(),
            created_at=datetime.now(),
            amount=10,
            currency="USD",
            payment_method_ids=[payment_method_id],
        ),
        created_at=datetime.now(),
        confirmable=False,
        payment_operations=[
            factories.PaymentOperationFactory(
                created_at=datetime.now(),
                payment_method_id=payment_method_id,
                type=enums.OperationTypeEnum.INITIALIZE,
                status=enums.OperationStatusEnum.STARTED,
            ),
        ],
    )

    with pytest.raises(ValueError):
        FakeSaga(
            unit_of_work=fake_unit_of_work(
                payment_method_repository_class=fake_payment_method_repository_class([]),
                payment_operation_repository_class=fake_payment_operation_repository_class(set()),
                block_event_repository_class=fake_block_event_repository_class(set()),
                transaction_repository_class=fake_transaction_repository_class(set()),
            )
        ).do_something(payment_method=payment_method)
