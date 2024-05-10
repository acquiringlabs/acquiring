from typing import Callable, Optional

from acquiring import domain, protocols


def test_givenCorrectInformation_paymentFlowGetsDefined(
    fake_payment_method_repository_class: Callable[
        [Optional[list[protocols.PaymentMethod]]], type[protocols.Repository]
    ],
    fake_payment_operation_repository: type[protocols.Repository],
    fake_block: type[protocols.Block],
    fake_process_action_block: type[protocols.Block],
    fake_unit_of_work: type[protocols.UnitOfWork],
) -> None:

    def fake_payment_flow() -> protocols.PaymentFlow:

        return domain.PaymentFlow(
            unit_of_work=fake_unit_of_work(
                payment_method_repository_class=fake_payment_method_repository_class([]),
            ),
            payment_operation_repository=fake_payment_operation_repository(),
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
