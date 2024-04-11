from typing import Type

from acquiring import domain, protocols


def test_givenCorrectInformation_paymentFlowGetsDefined(
    fake_payment_method_repository: Type[protocols.Repository],
    fake_payment_operation_repository: Type[protocols.Repository],
    fake_block: Type[protocols.Block],
    fake_process_action_block: Type[protocols.Block],
) -> None:

    def fake_payment_flow() -> protocols.PaymentFlow:

        return domain.PaymentFlow(
            payment_method_repository=fake_payment_method_repository(),
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
