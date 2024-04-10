import uuid
from datetime import datetime

import pytest

from acquiring import domain, enums, protocols
from tests.domain import factories

# See fixtures specifics for these tests below


def test_paymentMethodWithoutPaymentOperationsCanInitialize() -> None:
    """A Payment Method that has no payment operations can go through initialize."""
    assert (
        domain.flow.dl.can_initialize(
            domain.PaymentMethod(
                id=uuid.uuid4(),
                payment_attempt=factories.PaymentAttemptFactory(),
                created_at=datetime.now(),
                confirmable=True,
            )
        )
        is True
    )


def test_paymentMethodWithStartedInitializePOCannotInitialize(
    payment_operation_initialize_started: protocols.AbstractPaymentOperation,
) -> None:
    """A Payment Method that has already started initialized cannot go through initialize."""
    assert (
        domain.flow.dl.can_initialize(
            domain.PaymentMethod(
                id=uuid.uuid4(),
                payment_attempt=factories.PaymentAttemptFactory(),
                created_at=datetime.now(),
                confirmable=True,
                payment_operations=[
                    payment_operation_initialize_started,
                ],
            )
        )
        is False
    )


@pytest.mark.parametrize(
    "status",
    [
        status
        for status in enums.OperationStatusEnum
        if status not in (enums.OperationStatusEnum.STARTED, enums.OperationStatusEnum.PENDING)
    ],
)
def test_paymentMethodAlreadyInitializedCannotInitialize(
    payment_operation_initialize_started: protocols.AbstractPaymentOperation,
    status: protocols.AbstractPaymentOperation,
) -> None:
    """A Payment Method that has already completed initialized cannot go through initialize."""
    assert (
        domain.flow.dl.can_initialize(
            domain.PaymentMethod(
                id=uuid.uuid4(),
                payment_attempt=factories.PaymentAttemptFactory(),
                created_at=datetime.now(),
                confirmable=True,
                payment_operations=[
                    payment_operation_initialize_started,
                    factories.PaymentOperationFactory(
                        payment_method_id=uuid.uuid4(),
                        type=enums.OperationTypeEnum.INITIALIZE,
                        status=status,
                    ),
                ],
            )
        )
        is False
    )


### DECISION LOGIC SPECIFIC FIXTURES


@pytest.fixture(scope="module")
def payment_operation_initialize_started() -> protocols.AbstractPaymentOperation:

    return factories.PaymentOperationFactory(
        payment_method_id=uuid.uuid4(),
        type=enums.OperationTypeEnum.INITIALIZE,
        status=enums.OperationStatusEnum.STARTED,
    )


@pytest.fixture(scope="module")
def payment_operation_initialize_completed() -> protocols.AbstractPaymentOperation:

    return factories.PaymentOperationFactory(
        payment_method_id=uuid.uuid4(),
        type=enums.OperationTypeEnum.INITIALIZE,
        status=enums.OperationStatusEnum.COMPLETED,
    )


@pytest.fixture(scope="module")
def payment_operation_initialize_failed() -> protocols.AbstractPaymentOperation:

    return factories.PaymentOperationFactory(
        payment_method_id=uuid.uuid4(),
        type=enums.OperationTypeEnum.INITIALIZE,
        status=enums.OperationStatusEnum.FAILED,
    )


@pytest.fixture(scope="module")
def payment_operation_initialize_requires_action() -> protocols.AbstractPaymentOperation:

    return factories.PaymentOperationFactory(
        payment_method_id=uuid.uuid4(),
        type=enums.OperationTypeEnum.INITIALIZE,
        status=enums.OperationStatusEnum.REQUIRES_ACTION,
    )


@pytest.fixture(scope="module")
def payment_operation_initialize_not_performed() -> protocols.AbstractPaymentOperation:

    return factories.PaymentOperationFactory(
        payment_method_id=uuid.uuid4(),
        type=enums.OperationTypeEnum.INITIALIZE,
        status=enums.OperationStatusEnum.NOT_PERFORMED,
    )
