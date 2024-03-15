import pytest

from django_acquiring.flows import PaymentFlow
from django_acquiring.payments.models import PaymentOperation as DbPaymentOperation
from django_acquiring.protocols.payments import PaymentOperationStatusEnum, PaymentOperationTypeEnum
from tests.factories import PaymentAttemptFactory, PaymentMethodFactory

COMPLETED_STATUS = [PaymentOperationStatusEnum.completed]

PENDING_STATUS = [PaymentOperationStatusEnum.pending]

FAILED_STATUS = [
    PaymentOperationStatusEnum.started,
    PaymentOperationStatusEnum.requires_action,
    PaymentOperationStatusEnum.failed,
]


def test_statusListsAreComplete():
    assert set(COMPLETED_STATUS + PENDING_STATUS + FAILED_STATUS) == set(PaymentOperationStatusEnum)


@pytest.mark.django_db
@pytest.mark.parametrize(
    "result_status, payment_operation_status",
    [(PaymentOperationStatusEnum.completed, status) for status in COMPLETED_STATUS]
    + [(PaymentOperationStatusEnum.pending, status) for status in PENDING_STATUS]
    + [(PaymentOperationStatusEnum.failed, status) for status in FAILED_STATUS],
)
def test_givenAValidPaymentMethod_whenInitializingCompletes_thenPaymentFlowCallsPayAndReturnsTheCorrectOperationResponse(
    fake_payment_method_repository,
    fake_payment_operation_repository,
    fake_initialize_block,
    fake_process_actions_block,
    fake_pay_block,
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
        initialize_block=fake_initialize_block(
            fake_response_status=PaymentOperationStatusEnum.completed,
            fake_response_actions=[],
        ),
        process_actions_block=fake_process_actions_block(),
        pay_blocks=[fake_pay_block(fake_response_status=payment_operation_status)],
    )

    result = payment_flow.initialize(db_payment_method.to_domain())

    # then the payment flow returns the correct Operation Response
    assert DbPaymentOperation.objects.count() == 4
    db_payment_operations = DbPaymentOperation.objects.order_by("created_at").all()
    assert db_payment_operations[0].type == PaymentOperationTypeEnum.initialize
    assert db_payment_operations[0].status == PaymentOperationStatusEnum.started

    assert db_payment_operations[1].type == PaymentOperationTypeEnum.initialize
    assert db_payment_operations[1].status == PaymentOperationStatusEnum.completed

    assert db_payment_operations[2].type == PaymentOperationTypeEnum.pay
    assert db_payment_operations[2].status == PaymentOperationStatusEnum.started

    assert db_payment_operations[3].type == PaymentOperationTypeEnum.pay
    assert db_payment_operations[3].status == result_status

    assert result.payment_operation_type == PaymentOperationTypeEnum.pay
    assert result.status == result_status
    assert result.actions == []
    assert result.payment_method.id == db_payment_method.id
