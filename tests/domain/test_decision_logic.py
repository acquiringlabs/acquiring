import uuid
from datetime import datetime

import pytest

from acquiring import domain, enums, protocols
from tests.domain import factories

# See fixtures specifics for these tests below


class TestCanInitialize:

    def test_paymentMethodWithoutPaymentOperationsCanInitialize(self) -> None:
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
        self,
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
        self,
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


class TestCanProcessAction:

    def test_paymentMethodRequiringActionCanProcessAction(
        self,
        payment_operation_initialize_started: protocols.AbstractPaymentOperation,
        payment_operation_initialize_requires_action: protocols.AbstractPaymentOperation,
    ) -> None:
        """A Payment Method that has already started initialization and ended requiring actions can go through,"""
        assert (
            domain.flow.dl.can_process_action(
                domain.PaymentMethod(
                    id=uuid.uuid4(),
                    payment_attempt=factories.PaymentAttemptFactory(),
                    created_at=datetime.now(),
                    confirmable=False,
                    payment_operations=[
                        payment_operation_initialize_started,
                        payment_operation_initialize_requires_action,
                    ],
                )
            )
            is True
        )

    def test_paymentMethodAlreadyStartedProcessActionCannotProcessAction(
        self,
        payment_operation_initialize_started: protocols.AbstractPaymentOperation,
        payment_operation_initialize_requires_action: protocols.AbstractPaymentOperation,
        payment_operation_process_action_started: protocols.AbstractPaymentOperation,
    ) -> None:
        """A Payment Method that has already started process_action cannot go through process_action."""
        assert (
            domain.flow.dl.can_process_action(
                domain.PaymentMethod(
                    id=uuid.uuid4(),
                    payment_attempt=factories.PaymentAttemptFactory(),
                    created_at=datetime.now(),
                    confirmable=False,
                    payment_operations=[
                        payment_operation_initialize_started,
                        payment_operation_initialize_requires_action,
                        payment_operation_process_action_started,
                    ],
                )
            )
            is False
        )

    def test_paymentMethodNotInitializedCannotProcessAction(
        self,
        payment_operation_initialize_started: protocols.AbstractPaymentOperation,
    ) -> None:
        """A Payment Method that has not performed initialize cannot go through process_action."""
        assert (
            domain.flow.dl.can_process_action(
                domain.PaymentMethod(
                    id=uuid.uuid4(),
                    payment_attempt=factories.PaymentAttemptFactory(),
                    created_at=datetime.now(),
                    confirmable=False,
                    payment_operations=[
                        payment_operation_initialize_started,
                    ],
                )
            )
            is False
        )

    @pytest.mark.parametrize(
        "not_requires_action_status",
        [
            status
            for status in enums.OperationStatusEnum
            if status not in (enums.OperationStatusEnum.STARTED, enums.OperationStatusEnum.REQUIRES_ACTION)
        ],
    )
    def test_paymentMethodInitializedWithoutRequiresActionCannotProcessAction(
        self,
        payment_operation_initialize_started: protocols.AbstractPaymentOperation,
        not_requires_action_status: enums.OperationStatusEnum,
    ) -> None:
        """A Payment Method that has not performed initialize cannot go through process_action."""
        assert (
            domain.flow.dl.can_process_action(
                domain.PaymentMethod(
                    id=uuid.uuid4(),
                    payment_attempt=factories.PaymentAttemptFactory(),
                    created_at=datetime.now(),
                    confirmable=False,
                    payment_operations=[
                        payment_operation_initialize_started,
                        factories.PaymentOperationFactory(
                            payment_method_id=uuid.uuid4(),
                            type=enums.OperationTypeEnum.INITIALIZE,
                            status=not_requires_action_status,
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


@pytest.fixture(scope="module")
def payment_operation_process_action_started() -> protocols.AbstractPaymentOperation:
    return factories.PaymentOperationFactory(
        payment_method_id=uuid.uuid4(),
        type=enums.OperationTypeEnum.PROCESS_ACTION,
        status=enums.OperationStatusEnum.STARTED,
    )
