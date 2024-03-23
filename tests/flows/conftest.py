from typing import Sequence, Type

import pytest

from django_acquiring import domain
from django_acquiring.enums import OperationStatusEnum
from django_acquiring.protocols.flows import AbstractBlock, AbstractBlockResponse
from django_acquiring.protocols.payments import AbstractPaymentMethod


@pytest.fixture(scope="module")
def fake_block() -> Type[AbstractBlock]:
    class FakeBlock:

        def __init__(
            self,
            *args: Sequence,
            **kwargs: dict,
        ):
            fake_response_status: OperationStatusEnum = kwargs.get(
                "fake_response_status", OperationStatusEnum.COMPLETED
            )  # type:ignore[assignment]

            fake_response_actions: list[dict] = kwargs.get("fake_response_actions", [])  # type:ignore[assignment]

            self.response_status = fake_response_status
            self.response_actions = fake_response_actions or []

        def run(self, payment_method: AbstractPaymentMethod, *args: Sequence, **kwargs: dict) -> AbstractBlockResponse:
            return domain.BlockResponse(
                status=self.response_status,
                actions=self.response_actions,
                payment_method=payment_method,
            )

    assert issubclass(FakeBlock, AbstractBlock)
    return FakeBlock


@pytest.fixture(scope="module")
def fake_process_action_block() -> Type[AbstractBlock]:

    class FakeProcessActionsBlock:

        def __init__(
            self,
            fake_response_status: OperationStatusEnum = OperationStatusEnum.COMPLETED,
        ):
            self.response_status = fake_response_status

        def run(self, payment_method: AbstractPaymentMethod, *args: Sequence, **kwargs: dict) -> AbstractBlockResponse:
            return domain.BlockResponse(status=self.response_status, payment_method=payment_method)

    assert issubclass(FakeProcessActionsBlock, AbstractBlock)
    return FakeProcessActionsBlock
