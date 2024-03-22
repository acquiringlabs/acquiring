from typing import Dict, List, Sequence, Type

import pytest

from django_acquiring import domain
from django_acquiring.protocols.enums import OperationStatusEnum
from django_acquiring.protocols.flows import AbstractBlock, AbstractBlockResponse
from django_acquiring.protocols.payments import AbstractPaymentMethod


# TODO Remove all  # type:ignore[call-arg] from arguments in tests
@pytest.fixture(scope="module")
def fake_block() -> Type[AbstractBlock]:
    class FakeBlock:

        def __init__(
            self,
            fake_response_status: OperationStatusEnum = OperationStatusEnum.completed,
            fake_response_actions: List[Dict] | None = None,
        ):
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
def fake_process_actions_block() -> Type[AbstractBlock]:

    class FakeProcessActionsBlock:

        def __init__(
            self,
            fake_response_status: OperationStatusEnum = OperationStatusEnum.completed,
        ):
            self.response_status = fake_response_status

        def run(self, payment_method: AbstractPaymentMethod, *args: Sequence, **kwargs: Dict) -> AbstractBlockResponse:
            return domain.BlockResponse(status=self.response_status, payment_method=payment_method)

    assert issubclass(FakeProcessActionsBlock, AbstractBlock)
    return FakeProcessActionsBlock
