from typing import Callable, Optional

from acquiring import domain, protocols
from tests import protocols as test_protocols


def test_givenCorrectInformation_paymentSagaGetsDefined(
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
    fake_block: type[protocols.Block],
    fake_process_action_block: type[protocols.Block],
    fake_unit_of_work: type[test_protocols.FakeUnitOfWork],
) -> None:

    def fake_payment_flow() -> protocols.PaymentSaga:

        return domain.PaymentSaga(
            unit_of_work=fake_unit_of_work(
                payment_method_repository_class=fake_payment_method_repository_class([]),
                payment_operation_repository_class=fake_payment_operation_repository_class(set()),
                block_event_repository_class=fake_block_event_repository_class(set()),
                transaction_repository_class=fake_transaction_repository_class(set()),
            ),
            initialize_block=fake_block(),
            process_action_block=fake_process_action_block(),
            pay_blocks=[
                fake_block(),
            ],
            after_pay_blocks=[
                fake_block(),
            ],
            confirm_block=fake_block(),
            after_confirm_blocks=[fake_block()],
        )

    fake_payment_flow()
