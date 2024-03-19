import pytest

from django_acquiring.flows import PaymentFlow
from django_acquiring.payments import models
from django_acquiring.protocols.enums import OperationStatusEnum, OperationTypeEnum
from tests.factories import PaymentAttemptFactory, PaymentMethodFactory

COMPLETED_STATUS = [OperationStatusEnum.completed]

PENDING_STATUS = [OperationStatusEnum.pending]

FAILED_STATUS = [
    OperationStatusEnum.started,
    OperationStatusEnum.requires_action,
    OperationStatusEnum.failed,
]


def test_statusListsAreComplete():
    assert set(COMPLETED_STATUS + PENDING_STATUS + FAILED_STATUS) == set(OperationStatusEnum)


@pytest.mark.django_db
@pytest.mark.parametrize(
    "result_status, payment_operation_status",
    [(OperationStatusEnum.completed, status) for status in COMPLETED_STATUS]
    + [(OperationStatusEnum.pending, status) for status in PENDING_STATUS]
    + [(OperationStatusEnum.failed, status) for status in FAILED_STATUS],
)
def test_givenAValidPaymentMethod_whenInitializeCompletes_thenPaymentFlowCallsPayAndReturnsTheCorrectOperationResponse(
    fake_payment_method_repository,
    fake_payment_operation_repository,
    fake_block,
    fake_process_actions_block,
    result_status,
    payment_operation_status,
):
    # given a valid payment attempt
    db_payment_attempt = PaymentAttemptFactory.create()
    db_payment_method = PaymentMethodFactory.create(payment_attempt_id=db_payment_attempt.id)

    # when Initializing
    payment_method_repository = fake_payment_method_repository(db_payment_methods=[db_payment_method])
    payment_flow = PaymentFlow(
        repository=payment_method_repository,
        operations_repository=fake_payment_operation_repository(),
        initialize_block=fake_block(
            fake_response_status=OperationStatusEnum.completed,
            fake_response_actions=[],
        ),
        process_actions_block=fake_process_actions_block(),
        pay_blocks=[fake_block(fake_response_status=payment_operation_status)],
        after_pay_blocks=[],
        confirm_blocks=[],
    )

    result = payment_flow.initialize(db_payment_method.to_domain())

    # then the payment flow returns the correct Operation Response
    assert models.PaymentOperation.objects.count() == 4
    db_payment_operations = models.PaymentOperation.objects.order_by("created_at").all()
    assert db_payment_operations[0].type == OperationTypeEnum.initialize
    assert db_payment_operations[0].status == OperationStatusEnum.started

    assert db_payment_operations[1].type == OperationTypeEnum.initialize
    assert db_payment_operations[1].status == OperationStatusEnum.completed

    assert db_payment_operations[2].type == OperationTypeEnum.pay
    assert db_payment_operations[2].status == OperationStatusEnum.started

    assert db_payment_operations[3].type == OperationTypeEnum.pay
    assert db_payment_operations[3].status == result_status

    assert result.type == OperationTypeEnum.pay
    assert result.status == result_status
    assert result.actions == []
    assert result.payment_method.id == db_payment_method.id
