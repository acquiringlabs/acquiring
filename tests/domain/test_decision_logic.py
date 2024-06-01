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
            domain.sagas.dl.can_initialize(
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
        payment_operation_initialize_started: protocols.PaymentOperation,
    ) -> None:
        """A Payment Method that has already started initialized cannot go through initialize."""
        assert (
            domain.sagas.dl.can_initialize(
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
        payment_operation_initialize_started: protocols.PaymentOperation,
        status: protocols.PaymentOperation,
    ) -> None:
        """A Payment Method that has already completed initialized cannot go through initialize."""
        assert (
            domain.sagas.dl.can_initialize(
                domain.PaymentMethod(
                    id=uuid.uuid4(),
                    payment_attempt=factories.PaymentAttemptFactory(),
                    created_at=datetime.now(),
                    confirmable=True,
                    payment_operations=[
                        payment_operation_initialize_started,
                        factories.PaymentOperationFactory(
                            created_at=datetime.now(),
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
        payment_operation_initialize_started: protocols.PaymentOperation,
        payment_operation_initialize_requires_action: protocols.PaymentOperation,
    ) -> None:
        """A Payment Method that has already started initialization and ended requiring actions can go through,"""
        assert (
            domain.sagas.dl.can_process_action(
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
        payment_operation_initialize_started: protocols.PaymentOperation,
        payment_operation_initialize_requires_action: protocols.PaymentOperation,
        payment_operation_process_action_started: protocols.PaymentOperation,
    ) -> None:
        """A Payment Method that has already started process_action cannot go through process_action."""
        assert (
            domain.sagas.dl.can_process_action(
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
        payment_operation_initialize_started: protocols.PaymentOperation,
    ) -> None:
        """A Payment Method that has not performed initialize cannot go through process_action."""
        assert (
            domain.sagas.dl.can_process_action(
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
        payment_operation_initialize_started: protocols.PaymentOperation,
        not_requires_action_status: enums.OperationStatusEnum,
    ) -> None:
        """A Payment Method that has not performed initialize cannot go through process_action."""
        assert (
            domain.sagas.dl.can_process_action(
                domain.PaymentMethod(
                    id=uuid.uuid4(),
                    payment_attempt=factories.PaymentAttemptFactory(),
                    created_at=datetime.now(),
                    confirmable=False,
                    payment_operations=[
                        payment_operation_initialize_started,
                        factories.PaymentOperationFactory(
                            created_at=datetime.now(),
                            payment_method_id=uuid.uuid4(),
                            type=enums.OperationTypeEnum.INITIALIZE,
                            status=not_requires_action_status,
                        ),
                    ],
                )
            )
            is False
        )


class TestCanAfterPay:

    def test_paymentMethodInitializedViaCompleteAndPaidCanAfterPay(
        self,
        payment_operation_initialize_started: protocols.PaymentOperation,
        payment_operation_initialize_completed: protocols.PaymentOperation,
        payment_operation_pay_started: protocols.PaymentOperation,
        payment_operation_pay_completed: protocols.PaymentOperation,
    ) -> None:
        """A Payment Method that has already initialized and has already pay can go through."""
        assert (
            domain.sagas.dl.can_after_pay(
                domain.PaymentMethod(
                    id=uuid.uuid4(),
                    payment_attempt=factories.PaymentAttemptFactory(),
                    created_at=datetime.now(),
                    confirmable=False,
                    payment_operations=[
                        payment_operation_initialize_started,
                        payment_operation_initialize_completed,
                        payment_operation_pay_started,
                        payment_operation_pay_completed,
                    ],
                )
            )
            is True
        )

    def test_paymentMethodInitializedViaRequiresActionAndPaidCanAfterPay(
        self,
        payment_operation_initialize_started: protocols.PaymentOperation,
        payment_operation_initialize_requires_action: protocols.PaymentOperation,
        payment_operation_process_action_started: protocols.PaymentOperation,
        payment_operation_process_action_completed: protocols.PaymentOperation,
        payment_operation_pay_started: protocols.PaymentOperation,
        payment_operation_pay_completed: protocols.PaymentOperation,
    ) -> None:
        """A Payment Method that has already initialized via process action and has already pay can go through."""
        assert (
            domain.sagas.dl.can_after_pay(
                domain.PaymentMethod(
                    id=uuid.uuid4(),
                    payment_attempt=factories.PaymentAttemptFactory(),
                    created_at=datetime.now(),
                    confirmable=False,
                    payment_operations=[
                        payment_operation_initialize_started,
                        payment_operation_initialize_requires_action,
                        payment_operation_process_action_started,
                        payment_operation_process_action_completed,
                        payment_operation_pay_started,
                        payment_operation_pay_completed,
                    ],
                )
            )
            is True
        )

    def test_paymentMethodInitializedViaNotPerformedAndPaidCanAfterPay(
        self,
        payment_operation_initialize_started: protocols.PaymentOperation,
        payment_operation_initialize_not_performed: protocols.PaymentOperation,
        payment_operation_pay_started: protocols.PaymentOperation,
        payment_operation_pay_completed: protocols.PaymentOperation,
    ) -> None:
        """A Payment Method that has not performed initialized and has already pay can go through."""
        assert (
            domain.sagas.dl.can_after_pay(
                domain.PaymentMethod(
                    id=uuid.uuid4(),
                    payment_attempt=factories.PaymentAttemptFactory(),
                    created_at=datetime.now(),
                    confirmable=False,
                    payment_operations=[
                        payment_operation_initialize_started,
                        payment_operation_initialize_not_performed,
                        payment_operation_pay_started,
                        payment_operation_pay_completed,
                    ],
                )
            )
            is True
        )

    def test_paymentMethodNotInitializedCannotAfterPay(
        self,
        payment_operation_initialize_started: protocols.PaymentOperation,
    ) -> None:
        """A Payment Method that has not completed initialization cannot go through"""
        assert (
            domain.sagas.dl.can_after_pay(
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

    def test_paymentMethodInitializeFailedCannotAfterPay(
        self,
        payment_operation_initialize_started: protocols.PaymentOperation,
        payment_operation_initialize_failed: protocols.PaymentOperation,
    ) -> None:
        """A Payment Method that has not completed initialization cannot go through"""
        assert (
            domain.sagas.dl.can_after_pay(
                domain.PaymentMethod(
                    id=uuid.uuid4(),
                    payment_attempt=factories.PaymentAttemptFactory(),
                    created_at=datetime.now(),
                    confirmable=False,
                    payment_operations=[
                        payment_operation_initialize_started,
                        payment_operation_initialize_failed,
                    ],
                )
            )
            is False
        )

    def test_paymentMethodInitializedButNotPaidCannotAfterPay(
        self,
        payment_operation_initialize_started: protocols.PaymentOperation,
        payment_operation_initialize_not_performed: protocols.PaymentOperation,
        payment_operation_pay_started: protocols.PaymentOperation,
    ) -> None:
        """A Payment Method that has not completed pay cannot go through."""
        assert (
            domain.sagas.dl.can_after_pay(
                domain.PaymentMethod(
                    id=uuid.uuid4(),
                    payment_attempt=factories.PaymentAttemptFactory(),
                    created_at=datetime.now(),
                    confirmable=False,
                    payment_operations=[
                        payment_operation_initialize_started,
                        payment_operation_initialize_not_performed,
                        payment_operation_pay_started,
                    ],
                )
            )
            is False
        )

    def test_paymentMethodInitializedButNotFailedPaidCannotAfterPay(
        self,
        payment_operation_initialize_started: protocols.PaymentOperation,
        payment_operation_initialize_not_performed: protocols.PaymentOperation,
        payment_operation_pay_started: protocols.PaymentOperation,
        payment_operation_pay_failed: protocols.PaymentOperation,
    ) -> None:
        """A Payment Method that has not completed pay cannot go through."""
        assert (
            domain.sagas.dl.can_after_pay(
                domain.PaymentMethod(
                    id=uuid.uuid4(),
                    payment_attempt=factories.PaymentAttemptFactory(),
                    created_at=datetime.now(),
                    confirmable=False,
                    payment_operations=[
                        payment_operation_initialize_started,
                        payment_operation_initialize_not_performed,
                        payment_operation_pay_started,
                        payment_operation_pay_failed,
                    ],
                )
            )
            is False
        )

    def test_paymentMethodAlreadyStartedAfterPayCannotAfterPay(
        self,
        payment_operation_initialize_started: protocols.PaymentOperation,
        payment_operation_initialize_not_performed: protocols.PaymentOperation,
        payment_operation_pay_started: protocols.PaymentOperation,
        payment_operation_pay_completed: protocols.PaymentOperation,
        payment_operation_after_pay_started: protocols.PaymentOperation,
    ) -> None:
        """A Payment Method that has already started after pay cannot go through"""
        assert (
            domain.sagas.dl.can_after_pay(
                domain.PaymentMethod(
                    id=uuid.uuid4(),
                    payment_attempt=factories.PaymentAttemptFactory(),
                    created_at=datetime.now(),
                    confirmable=False,
                    payment_operations=[
                        payment_operation_initialize_started,
                        payment_operation_initialize_not_performed,
                        payment_operation_pay_started,
                        payment_operation_pay_completed,
                        payment_operation_after_pay_started,
                    ],
                )
            )
            is False
        )


class TestCanConfirm:

    def test_paymentMethodConfirmableAndAfterPayCompletedCanConfirm(
        self,
        payment_operation_initialize_started: protocols.PaymentOperation,
        payment_operation_initialize_not_performed: protocols.PaymentOperation,
        payment_operation_pay_started: protocols.PaymentOperation,
        payment_operation_pay_completed: protocols.PaymentOperation,
        payment_operation_after_pay_started: protocols.PaymentOperation,
        payment_operation_after_pay_completed: protocols.PaymentOperation,
    ) -> None:
        """A Payment Method that is confirmable and has completed pay can go through."""
        assert (
            domain.sagas.dl.can_confirm(
                domain.PaymentMethod(
                    id=uuid.uuid4(),
                    payment_attempt=factories.PaymentAttemptFactory(),
                    created_at=datetime.now(),
                    confirmable=True,
                    payment_operations=[
                        payment_operation_initialize_started,
                        payment_operation_initialize_not_performed,
                        payment_operation_pay_started,
                        payment_operation_pay_completed,
                        payment_operation_after_pay_started,
                        payment_operation_after_pay_completed,
                    ],
                )
            )
            is True
        )

    @pytest.mark.parametrize(
        "non_completed_after_pay_status",
        [status for status in enums.OperationStatusEnum if status != enums.OperationStatusEnum.COMPLETED],
    )
    def test_paymentMethodConfirmableAndAfterPayFinishedWithNonCompletedStatusCanConfirm(
        self,
        payment_operation_initialize_started: protocols.PaymentOperation,
        payment_operation_initialize_not_performed: protocols.PaymentOperation,
        payment_operation_pay_started: protocols.PaymentOperation,
        payment_operation_pay_completed: protocols.PaymentOperation,
        payment_operation_after_pay_started: protocols.PaymentOperation,
        non_completed_after_pay_status: enums.OperationStatusEnum,
    ) -> None:
        """A Payment Method that is confirmable and has completed pay can go through."""
        assert (
            domain.sagas.dl.can_confirm(
                domain.PaymentMethod(
                    id=uuid.uuid4(),
                    payment_attempt=factories.PaymentAttemptFactory(),
                    created_at=datetime.now(),
                    confirmable=True,
                    payment_operations=[
                        payment_operation_initialize_started,
                        payment_operation_initialize_not_performed,
                        payment_operation_pay_started,
                        payment_operation_pay_completed,
                        payment_operation_after_pay_started,
                        factories.PaymentOperationFactory(
                            created_at=datetime.now(),
                            payment_method_id=uuid.uuid4(),
                            type=enums.OperationTypeEnum.AFTER_PAY,
                            status=non_completed_after_pay_status,
                        ),
                    ],
                )
            )
            is False
        )

    def test_paymentMethodNonConfirmableAndAfterPayCompletedCannotConfirm(
        self,
        payment_operation_initialize_started: protocols.PaymentOperation,
        payment_operation_initialize_not_performed: protocols.PaymentOperation,
        payment_operation_pay_started: protocols.PaymentOperation,
        payment_operation_pay_completed: protocols.PaymentOperation,
        payment_operation_after_pay_started: protocols.PaymentOperation,
        payment_operation_after_pay_completed: protocols.PaymentOperation,
    ) -> None:
        """A Payment Method that is NOT confirmable and has completed pay cannot go through."""
        assert (
            domain.sagas.dl.can_confirm(
                domain.PaymentMethod(
                    id=uuid.uuid4(),
                    payment_attempt=factories.PaymentAttemptFactory(),
                    created_at=datetime.now(),
                    confirmable=False,
                    payment_operations=[
                        payment_operation_initialize_started,
                        payment_operation_initialize_not_performed,
                        payment_operation_pay_started,
                        payment_operation_pay_completed,
                        payment_operation_after_pay_started,
                        payment_operation_after_pay_completed,
                    ],
                )
            )
            is False
        )

    def test_paymentMethodConfirmableAndConfirmStartedCannotConfirm(
        self,
        payment_operation_initialize_started: protocols.PaymentOperation,
        payment_operation_initialize_not_performed: protocols.PaymentOperation,
        payment_operation_pay_started: protocols.PaymentOperation,
        payment_operation_pay_completed: protocols.PaymentOperation,
        payment_operation_after_pay_started: protocols.PaymentOperation,
        payment_operation_after_pay_completed: protocols.PaymentOperation,
        payment_operation_confirm_started: protocols.PaymentOperation,
    ) -> None:
        """A Payment Method that is confirmable and has completed pay can go through."""
        assert (
            domain.sagas.dl.can_confirm(
                domain.PaymentMethod(
                    id=uuid.uuid4(),
                    payment_attempt=factories.PaymentAttemptFactory(),
                    created_at=datetime.now(),
                    confirmable=True,
                    payment_operations=[
                        payment_operation_initialize_started,
                        payment_operation_initialize_not_performed,
                        payment_operation_pay_started,
                        payment_operation_pay_completed,
                        payment_operation_after_pay_started,
                        payment_operation_after_pay_completed,
                        payment_operation_confirm_started,
                    ],
                )
            )
            is False
        )

    def test_paymentMethodConfirmableAndAfterPayNotCompletedCannotConfirm(
        self,
        payment_operation_initialize_started: protocols.PaymentOperation,
        payment_operation_initialize_not_performed: protocols.PaymentOperation,
        payment_operation_pay_started: protocols.PaymentOperation,
        payment_operation_pay_completed: protocols.PaymentOperation,
        payment_operation_after_pay_started: protocols.PaymentOperation,
    ) -> None:
        """A Payment Method that is confirmable and has not completed after pay, then cannot go through."""
        assert (
            domain.sagas.dl.can_confirm(
                domain.PaymentMethod(
                    id=uuid.uuid4(),
                    payment_attempt=factories.PaymentAttemptFactory(),
                    created_at=datetime.now(),
                    confirmable=True,
                    payment_operations=[
                        payment_operation_initialize_started,
                        payment_operation_initialize_not_performed,
                        payment_operation_pay_started,
                        payment_operation_pay_completed,
                        payment_operation_after_pay_started,
                    ],
                )
            )
            is False
        )

    def test_paymentMethodConfirmableAndPayCompletedCannotConfirm(
        self,
        payment_operation_initialize_started: protocols.PaymentOperation,
        payment_operation_initialize_not_performed: protocols.PaymentOperation,
        payment_operation_pay_started: protocols.PaymentOperation,
        payment_operation_pay_completed: protocols.PaymentOperation,
    ) -> None:
        """A Payment Method that is confirmable and has not completed after pay, then cannot go through."""
        assert (
            domain.sagas.dl.can_confirm(
                domain.PaymentMethod(
                    id=uuid.uuid4(),
                    payment_attempt=factories.PaymentAttemptFactory(),
                    created_at=datetime.now(),
                    confirmable=True,
                    payment_operations=[
                        payment_operation_initialize_started,
                        payment_operation_initialize_not_performed,
                        payment_operation_pay_started,
                        payment_operation_pay_completed,
                    ],
                )
            )
            is False
        )

    def test_paymentMethodConfirmableAndPayNotCompletedCannotConfirm(
        self,
        payment_operation_initialize_started: protocols.PaymentOperation,
        payment_operation_initialize_not_performed: protocols.PaymentOperation,
        payment_operation_pay_started: protocols.PaymentOperation,
    ) -> None:
        """A Payment Method that is confirmable and has not completed pay, then cannot go through."""
        assert (
            domain.sagas.dl.can_confirm(
                domain.PaymentMethod(
                    id=uuid.uuid4(),
                    payment_attempt=factories.PaymentAttemptFactory(),
                    created_at=datetime.now(),
                    confirmable=True,
                    payment_operations=[
                        payment_operation_initialize_started,
                        payment_operation_initialize_not_performed,
                        payment_operation_pay_started,
                    ],
                )
            )
            is False
        )

    def test_paymentMethodConfirmableAndPayNotStartedCannotConfirm(
        self,
        payment_operation_initialize_started: protocols.PaymentOperation,
        payment_operation_initialize_completed: protocols.PaymentOperation,
    ) -> None:
        """A Payment Method that is confirmable and has not completed initialize, then cannot go through."""
        assert (
            domain.sagas.dl.can_confirm(
                domain.PaymentMethod(
                    id=uuid.uuid4(),
                    payment_attempt=factories.PaymentAttemptFactory(),
                    created_at=datetime.now(),
                    confirmable=True,
                    payment_operations=[
                        payment_operation_initialize_started,
                        payment_operation_initialize_completed,
                    ],
                )
            )
            is False
        )


class TestCanAfterConfirm:

    def test_paymentMethodConfirmableAndConfirmCompletedCanAfterConfirm(
        self,
        payment_operation_initialize_started: protocols.PaymentOperation,
        payment_operation_initialize_not_performed: protocols.PaymentOperation,
        payment_operation_pay_started: protocols.PaymentOperation,
        payment_operation_pay_completed: protocols.PaymentOperation,
        payment_operation_after_pay_started: protocols.PaymentOperation,
        payment_operation_after_pay_completed: protocols.PaymentOperation,
        payment_operation_confirm_started: protocols.PaymentOperation,
        payment_operation_confirm_completed: protocols.PaymentOperation,
    ) -> None:
        """A Payment Method that has already initialized and has already pay and has already confirmed can go through."""
        assert (
            domain.sagas.dl.can_after_confirm(
                domain.PaymentMethod(
                    id=uuid.uuid4(),
                    payment_attempt=factories.PaymentAttemptFactory(),
                    created_at=datetime.now(),
                    confirmable=True,
                    payment_operations=[
                        payment_operation_initialize_started,
                        payment_operation_initialize_not_performed,
                        payment_operation_pay_started,
                        payment_operation_pay_completed,
                        payment_operation_after_pay_started,
                        payment_operation_after_pay_completed,
                        payment_operation_confirm_started,
                        payment_operation_confirm_completed,
                    ],
                )
            )
            is True
        )

    def test_paymentMethodNotConfirmableCannotAfterConfirm(
        self,
        payment_operation_initialize_started: protocols.PaymentOperation,
        payment_operation_initialize_not_performed: protocols.PaymentOperation,
        payment_operation_pay_started: protocols.PaymentOperation,
        payment_operation_pay_completed: protocols.PaymentOperation,
        payment_operation_after_pay_started: protocols.PaymentOperation,
        payment_operation_after_pay_completed: protocols.PaymentOperation,
        payment_operation_confirm_started: protocols.PaymentOperation,
        payment_operation_confirm_completed: protocols.PaymentOperation,
    ) -> None:
        """A Payment Method that is not confirmable cannot go through."""
        assert (
            domain.sagas.dl.can_after_confirm(
                domain.PaymentMethod(
                    id=uuid.uuid4(),
                    payment_attempt=factories.PaymentAttemptFactory(),
                    created_at=datetime.now(),
                    confirmable=False,
                    payment_operations=[
                        payment_operation_initialize_started,
                        payment_operation_initialize_not_performed,
                        payment_operation_pay_started,
                        payment_operation_pay_completed,
                        payment_operation_after_pay_started,
                        payment_operation_after_pay_completed,
                        payment_operation_confirm_started,
                        payment_operation_confirm_completed,
                    ],
                )
            )
            is False
        )

    @pytest.mark.parametrize(
        "non_completed_confirm_status",
        [status for status in enums.OperationStatusEnum if status != enums.OperationStatusEnum.COMPLETED],
    )
    def test_paymentMethodConfirmableAndConfirmHasNotCompletedCannotAfterConfirm(
        self,
        payment_operation_initialize_started: protocols.PaymentOperation,
        payment_operation_initialize_not_performed: protocols.PaymentOperation,
        payment_operation_pay_started: protocols.PaymentOperation,
        payment_operation_pay_completed: protocols.PaymentOperation,
        payment_operation_after_pay_started: protocols.PaymentOperation,
        payment_operation_after_pay_completed: protocols.PaymentOperation,
        payment_operation_confirm_started: protocols.PaymentOperation,
        non_completed_confirm_status: enums.OperationStatusEnum,
    ) -> None:
        """A Payment Method that has already initialized and has already pay and has already confirmed can go through."""
        assert (
            domain.sagas.dl.can_after_confirm(
                domain.PaymentMethod(
                    id=uuid.uuid4(),
                    payment_attempt=factories.PaymentAttemptFactory(),
                    created_at=datetime.now(),
                    confirmable=True,
                    payment_operations=[
                        payment_operation_initialize_started,
                        payment_operation_initialize_not_performed,
                        payment_operation_pay_started,
                        payment_operation_pay_completed,
                        payment_operation_after_pay_started,
                        payment_operation_after_pay_completed,
                        payment_operation_confirm_started,
                        factories.PaymentOperationFactory(
                            created_at=datetime.now(),
                            payment_method_id=uuid.uuid4(),
                            type=enums.OperationTypeEnum.CONFIRM,
                            status=non_completed_confirm_status,
                        ),
                    ],
                )
            )
            is False
        )

    def test_paymentMethodConfirmableAndAfterConfirmStartedCannotAfterConfirm(
        self,
        payment_operation_initialize_started: protocols.PaymentOperation,
        payment_operation_initialize_not_performed: protocols.PaymentOperation,
        payment_operation_pay_started: protocols.PaymentOperation,
        payment_operation_pay_completed: protocols.PaymentOperation,
        payment_operation_after_pay_started: protocols.PaymentOperation,
        payment_operation_after_pay_completed: protocols.PaymentOperation,
        payment_operation_confirm_started: protocols.PaymentOperation,
        payment_operation_confirm_completed: protocols.PaymentOperation,
        payment_operation_after_confirm_started: protocols.PaymentOperation,
    ) -> None:
        """A Payment Method that has already initialized and has already pay and has already confirmed can go through."""
        assert (
            domain.sagas.dl.can_after_confirm(
                domain.PaymentMethod(
                    id=uuid.uuid4(),
                    payment_attempt=factories.PaymentAttemptFactory(),
                    created_at=datetime.now(),
                    confirmable=True,
                    payment_operations=[
                        payment_operation_initialize_started,
                        payment_operation_initialize_not_performed,
                        payment_operation_pay_started,
                        payment_operation_pay_completed,
                        payment_operation_after_pay_started,
                        payment_operation_after_pay_completed,
                        payment_operation_confirm_started,
                        payment_operation_confirm_completed,
                        payment_operation_after_confirm_started,
                    ],
                )
            )
            is False
        )

    def test_paymentMethodConfirmableAndConfirmNotCompletedCannotAfterConfirm(
        self,
        payment_operation_initialize_started: protocols.PaymentOperation,
        payment_operation_initialize_not_performed: protocols.PaymentOperation,
        payment_operation_pay_started: protocols.PaymentOperation,
        payment_operation_pay_completed: protocols.PaymentOperation,
        payment_operation_after_pay_started: protocols.PaymentOperation,
        payment_operation_after_pay_completed: protocols.PaymentOperation,
        payment_operation_confirm_started: protocols.PaymentOperation,
    ) -> None:
        """A Payment Method that has already initialized and has already pay and has not confirmed cannot go through."""
        assert (
            domain.sagas.dl.can_after_confirm(
                domain.PaymentMethod(
                    id=uuid.uuid4(),
                    payment_attempt=factories.PaymentAttemptFactory(),
                    created_at=datetime.now(),
                    confirmable=True,
                    payment_operations=[
                        payment_operation_initialize_started,
                        payment_operation_initialize_not_performed,
                        payment_operation_pay_started,
                        payment_operation_pay_completed,
                        payment_operation_after_pay_started,
                        payment_operation_after_pay_completed,
                        payment_operation_confirm_started,
                    ],
                )
            )
            is False
        )

    def test_paymentMethodConfirmableAndAfterPayNotCompletedCannotAfterConfirm(
        self,
        payment_operation_initialize_started: protocols.PaymentOperation,
        payment_operation_initialize_not_performed: protocols.PaymentOperation,
        payment_operation_pay_started: protocols.PaymentOperation,
        payment_operation_pay_completed: protocols.PaymentOperation,
        payment_operation_after_pay_started: protocols.PaymentOperation,
    ) -> None:
        """A Payment Method that has already initialized and has already pay and has not after paid cannot go through."""
        assert (
            domain.sagas.dl.can_after_confirm(
                domain.PaymentMethod(
                    id=uuid.uuid4(),
                    payment_attempt=factories.PaymentAttemptFactory(),
                    created_at=datetime.now(),
                    confirmable=True,
                    payment_operations=[
                        payment_operation_initialize_started,
                        payment_operation_initialize_not_performed,
                        payment_operation_pay_started,
                        payment_operation_pay_completed,
                        payment_operation_after_pay_started,
                    ],
                )
            )
            is False
        )

    def test_paymentMethodConfirmableAndInitializeNotCompletedCannotAfterConfirm(
        self,
        payment_operation_initialize_started: protocols.PaymentOperation,
    ) -> None:
        """A Payment Method that has not initialized cannot go through."""
        assert (
            domain.sagas.dl.can_after_confirm(
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


class TestRefund:

    @pytest.mark.parametrize(
        "non_completed_after_pay_status",
        [status for status in enums.OperationStatusEnum if status != enums.OperationStatusEnum.COMPLETED],
    )
    def test_paymentMethodNotConfirmableAndAfterPayNotCompletedCannotRefund(
        self,
        payment_operation_initialize_started: protocols.PaymentOperation,
        payment_operation_initialize_completed: protocols.PaymentOperation,
        payment_operation_pay_started: protocols.PaymentOperation,
        payment_operation_pay_completed: protocols.PaymentOperation,
        payment_operation_after_pay_started: protocols.PaymentOperation,
        non_completed_after_pay_status: enums.OperationStatusEnum,
    ) -> None:
        assert (
            domain.sagas.dl.can_refund(
                domain.PaymentMethod(
                    id=uuid.uuid4(),
                    payment_attempt=factories.PaymentAttemptFactory(),
                    created_at=datetime.now(),
                    confirmable=False,
                    payment_operations=[
                        payment_operation_initialize_started,
                        payment_operation_initialize_completed,
                        payment_operation_pay_started,
                        payment_operation_pay_completed,
                        payment_operation_after_pay_started,
                        factories.PaymentOperationFactory(
                            created_at=datetime.now(),
                            payment_method_id=uuid.uuid4(),
                            type=enums.OperationTypeEnum.AFTER_PAY,
                            status=non_completed_after_pay_status,
                        ),
                    ],
                )
            )
            is False
        )

    def test_paymentMethodConfirmableAndAfterPayCompletedCannotRefund(
        self,
        payment_operation_initialize_started: protocols.PaymentOperation,
        payment_operation_initialize_completed: protocols.PaymentOperation,
        payment_operation_pay_started: protocols.PaymentOperation,
        payment_operation_pay_completed: protocols.PaymentOperation,
        payment_operation_after_pay_started: protocols.PaymentOperation,
        payment_operation_after_pay_completed: protocols.PaymentOperation,
    ) -> None:
        assert (
            domain.sagas.dl.can_refund(
                domain.PaymentMethod(
                    id=uuid.uuid4(),
                    payment_attempt=factories.PaymentAttemptFactory(),
                    created_at=datetime.now(),
                    confirmable=True,
                    payment_operations=[
                        payment_operation_initialize_started,
                        payment_operation_initialize_completed,
                        payment_operation_pay_started,
                        payment_operation_pay_completed,
                        payment_operation_after_pay_started,
                        payment_operation_after_pay_completed,
                    ],
                )
            )
            is False
        )

    def test_paymentMethodNotConfirmableAndAfterPayCompletedCanRefund(
        self,
        payment_operation_initialize_started: protocols.PaymentOperation,
        payment_operation_initialize_completed: protocols.PaymentOperation,
        payment_operation_pay_started: protocols.PaymentOperation,
        payment_operation_pay_completed: protocols.PaymentOperation,
        payment_operation_after_pay_started: protocols.PaymentOperation,
        payment_operation_after_pay_completed: protocols.PaymentOperation,
    ) -> None:
        assert (
            domain.sagas.dl.can_refund(
                domain.PaymentMethod(
                    id=uuid.uuid4(),
                    payment_attempt=factories.PaymentAttemptFactory(),
                    created_at=datetime.now(),
                    confirmable=False,
                    payment_operations=[
                        payment_operation_initialize_started,
                        payment_operation_initialize_completed,
                        payment_operation_pay_started,
                        payment_operation_pay_completed,
                        payment_operation_after_pay_started,
                        payment_operation_after_pay_completed,
                    ],
                )
            )
            is True
        )

    def test_paymentMethodConfirmableAndAfterConfirmCompletedCanRefund(
        self,
        payment_operation_initialize_started: protocols.PaymentOperation,
        payment_operation_initialize_completed: protocols.PaymentOperation,
        payment_operation_pay_started: protocols.PaymentOperation,
        payment_operation_pay_completed: protocols.PaymentOperation,
        payment_operation_after_pay_started: protocols.PaymentOperation,
        payment_operation_after_pay_completed: protocols.PaymentOperation,
        payment_operation_confirm_started: protocols.PaymentOperation,
        payment_operation_confirm_completed: protocols.PaymentOperation,
        payment_operation_after_confirm_started: protocols.PaymentOperation,
        payment_operation_after_confirm_completed: protocols.PaymentOperation,
    ) -> None:
        assert (
            domain.sagas.dl.can_refund(
                domain.PaymentMethod(
                    id=uuid.uuid4(),
                    payment_attempt=factories.PaymentAttemptFactory(),
                    created_at=datetime.now(),
                    confirmable=False,
                    payment_operations=[
                        payment_operation_initialize_started,
                        payment_operation_initialize_completed,
                        payment_operation_pay_started,
                        payment_operation_pay_completed,
                        payment_operation_after_pay_started,
                        payment_operation_after_pay_completed,
                        payment_operation_confirm_started,
                        payment_operation_confirm_completed,
                    ],
                )
            )
            is True
        )

    def test_paymentMethodNonConfirmableAndRefundStartedCannotRefund(
        self,
        payment_operation_initialize_started: protocols.PaymentOperation,
        payment_operation_initialize_completed: protocols.PaymentOperation,
        payment_operation_pay_started: protocols.PaymentOperation,
        payment_operation_pay_completed: protocols.PaymentOperation,
        payment_operation_after_pay_started: protocols.PaymentOperation,
        payment_operation_after_pay_completed: protocols.PaymentOperation,
        payment_operation_refund_started: protocols.PaymentOperation,
    ) -> None:
        assert (
            domain.sagas.dl.can_refund(
                domain.PaymentMethod(
                    id=uuid.uuid4(),
                    payment_attempt=factories.PaymentAttemptFactory(),
                    created_at=datetime.now(),
                    confirmable=False,
                    payment_operations=[
                        payment_operation_initialize_started,
                        payment_operation_initialize_completed,
                        payment_operation_pay_started,
                        payment_operation_pay_completed,
                        payment_operation_after_pay_started,
                        payment_operation_after_pay_completed,
                        payment_operation_refund_started,
                    ],
                )
            )
            is False
        )

    def test_paymentMethodNonConfirmableAndRefundCompletedCanRefundAgain(
        self,
        payment_operation_initialize_started: protocols.PaymentOperation,
        payment_operation_initialize_completed: protocols.PaymentOperation,
        payment_operation_pay_started: protocols.PaymentOperation,
        payment_operation_pay_completed: protocols.PaymentOperation,
        payment_operation_after_pay_started: protocols.PaymentOperation,
        payment_operation_after_pay_completed: protocols.PaymentOperation,
        payment_operation_refund_started: protocols.PaymentOperation,
        payment_operation_refund_completed: protocols.PaymentOperation,
    ) -> None:
        assert (
            domain.sagas.dl.can_refund(
                domain.PaymentMethod(
                    id=uuid.uuid4(),
                    payment_attempt=factories.PaymentAttemptFactory(),
                    created_at=datetime.now(),
                    confirmable=False,
                    payment_operations=[
                        payment_operation_initialize_started,
                        payment_operation_initialize_completed,
                        payment_operation_pay_started,
                        payment_operation_pay_completed,
                        payment_operation_after_pay_started,
                        payment_operation_after_pay_completed,
                        payment_operation_refund_started,
                        payment_operation_refund_completed,
                    ],
                )
            )
            is True
        )


### DECISION LOGIC SPECIFIC FIXTURES


@pytest.fixture(scope="module")
def payment_operation_initialize_started() -> protocols.PaymentOperation:
    return factories.PaymentOperationFactory(
        created_at=datetime.now(),
        payment_method_id=uuid.uuid4(),
        type=enums.OperationTypeEnum.INITIALIZE,
        status=enums.OperationStatusEnum.STARTED,
    )


@pytest.fixture(scope="module")
def payment_operation_initialize_completed() -> protocols.PaymentOperation:
    return factories.PaymentOperationFactory(
        created_at=datetime.now(),
        payment_method_id=uuid.uuid4(),
        type=enums.OperationTypeEnum.INITIALIZE,
        status=enums.OperationStatusEnum.COMPLETED,
    )


@pytest.fixture(scope="module")
def payment_operation_initialize_failed() -> protocols.PaymentOperation:
    return factories.PaymentOperationFactory(
        created_at=datetime.now(),
        payment_method_id=uuid.uuid4(),
        type=enums.OperationTypeEnum.INITIALIZE,
        status=enums.OperationStatusEnum.FAILED,
    )


@pytest.fixture(scope="module")
def payment_operation_initialize_requires_action() -> protocols.PaymentOperation:
    return factories.PaymentOperationFactory(
        created_at=datetime.now(),
        payment_method_id=uuid.uuid4(),
        type=enums.OperationTypeEnum.INITIALIZE,
        status=enums.OperationStatusEnum.REQUIRES_ACTION,
    )


@pytest.fixture(scope="module")
def payment_operation_initialize_not_performed() -> protocols.PaymentOperation:
    return factories.PaymentOperationFactory(
        created_at=datetime.now(),
        payment_method_id=uuid.uuid4(),
        type=enums.OperationTypeEnum.INITIALIZE,
        status=enums.OperationStatusEnum.NOT_PERFORMED,
    )


@pytest.fixture(scope="module")
def payment_operation_process_action_started() -> protocols.PaymentOperation:
    return factories.PaymentOperationFactory(
        created_at=datetime.now(),
        payment_method_id=uuid.uuid4(),
        type=enums.OperationTypeEnum.PROCESS_ACTION,
        status=enums.OperationStatusEnum.STARTED,
    )


@pytest.fixture(scope="module")
def payment_operation_process_action_completed() -> protocols.PaymentOperation:
    return factories.PaymentOperationFactory(
        created_at=datetime.now(),
        payment_method_id=uuid.uuid4(),
        type=enums.OperationTypeEnum.PROCESS_ACTION,
        status=enums.OperationStatusEnum.COMPLETED,
    )


@pytest.fixture(scope="module")
def payment_operation_pay_started() -> protocols.PaymentOperation:
    return factories.PaymentOperationFactory(
        created_at=datetime.now(),
        payment_method_id=uuid.uuid4(),
        type=enums.OperationTypeEnum.PAY,
        status=enums.OperationStatusEnum.STARTED,
    )


@pytest.fixture(scope="module")
def payment_operation_pay_completed() -> protocols.PaymentOperation:
    return factories.PaymentOperationFactory(
        created_at=datetime.now(),
        payment_method_id=uuid.uuid4(),
        type=enums.OperationTypeEnum.PAY,
        status=enums.OperationStatusEnum.COMPLETED,
    )


@pytest.fixture(scope="module")
def payment_operation_pay_failed() -> protocols.PaymentOperation:
    return factories.PaymentOperationFactory(
        created_at=datetime.now(),
        payment_method_id=uuid.uuid4(),
        type=enums.OperationTypeEnum.PAY,
        status=enums.OperationStatusEnum.FAILED,
    )


@pytest.fixture(scope="module")
def payment_operation_after_pay_started() -> protocols.PaymentOperation:
    return factories.PaymentOperationFactory(
        created_at=datetime.now(),
        payment_method_id=uuid.uuid4(),
        type=enums.OperationTypeEnum.AFTER_PAY,
        status=enums.OperationStatusEnum.STARTED,
    )


@pytest.fixture(scope="module")
def payment_operation_after_pay_completed() -> protocols.PaymentOperation:
    return factories.PaymentOperationFactory(
        created_at=datetime.now(),
        payment_method_id=uuid.uuid4(),
        type=enums.OperationTypeEnum.AFTER_PAY,
        status=enums.OperationStatusEnum.COMPLETED,
    )


@pytest.fixture(scope="module")
def payment_operation_confirm_started() -> protocols.PaymentOperation:
    return factories.PaymentOperationFactory(
        created_at=datetime.now(),
        payment_method_id=uuid.uuid4(),
        type=enums.OperationTypeEnum.CONFIRM,
        status=enums.OperationStatusEnum.STARTED,
    )


@pytest.fixture(scope="module")
def payment_operation_confirm_completed() -> protocols.PaymentOperation:
    return factories.PaymentOperationFactory(
        created_at=datetime.now(),
        payment_method_id=uuid.uuid4(),
        type=enums.OperationTypeEnum.CONFIRM,
        status=enums.OperationStatusEnum.COMPLETED,
    )


@pytest.fixture(scope="module")
def payment_operation_after_confirm_started() -> protocols.PaymentOperation:
    return factories.PaymentOperationFactory(
        created_at=datetime.now(),
        payment_method_id=uuid.uuid4(),
        type=enums.OperationTypeEnum.AFTER_CONFIRM,
        status=enums.OperationStatusEnum.STARTED,
    )


@pytest.fixture(scope="module")
def payment_operation_after_confirm_completed() -> protocols.PaymentOperation:
    return factories.PaymentOperationFactory(
        created_at=datetime.now(),
        payment_method_id=uuid.uuid4(),
        type=enums.OperationTypeEnum.AFTER_CONFIRM,
        status=enums.OperationStatusEnum.COMPLETED,
    )


@pytest.fixture(scope="module")
def payment_operation_refund_started() -> protocols.PaymentOperation:
    return factories.PaymentOperationFactory(
        created_at=datetime.now(),
        payment_method_id=uuid.uuid4(),
        type=enums.OperationTypeEnum.REFUND,
        status=enums.OperationStatusEnum.STARTED,
    )


@pytest.fixture(scope="module")
def payment_operation_refund_completed() -> protocols.PaymentOperation:
    return factories.PaymentOperationFactory(
        created_at=datetime.now(),
        payment_method_id=uuid.uuid4(),
        type=enums.OperationTypeEnum.REFUND,
        status=enums.OperationStatusEnum.COMPLETED,
    )


@pytest.fixture(scope="module")
def payment_operation_after_refund_started() -> protocols.PaymentOperation:
    return factories.PaymentOperationFactory(
        created_at=datetime.now(),
        payment_method_id=uuid.uuid4(),
        type=enums.OperationTypeEnum.AFTER_REFUND,
        status=enums.OperationStatusEnum.STARTED,
    )


@pytest.fixture(scope="module")
def payment_operation_after_refund_completed() -> protocols.PaymentOperation:
    return factories.PaymentOperationFactory(
        created_at=datetime.now(),
        payment_method_id=uuid.uuid4(),
        type=enums.OperationTypeEnum.AFTER_REFUND,
        status=enums.OperationStatusEnum.COMPLETED,
    )
