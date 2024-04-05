from typing import Sequence, Type

import pytest

from django_acquiring import domain, protocols
from django_acquiring.enums import OperationStatusEnum


@pytest.fixture(scope="module")
def fake_block() -> Type[protocols.AbstractBlock]:
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

        def run(
            self, payment_method: protocols.AbstractPaymentMethod, *args: Sequence, **kwargs: dict
        ) -> protocols.AbstractBlockResponse:
            return domain.BlockResponse(
                status=self.response_status,
                actions=self.response_actions,
            )

    assert issubclass(FakeBlock, protocols.AbstractBlock)
    return FakeBlock


@pytest.fixture(scope="module")
def fake_process_action_block() -> Type[protocols.AbstractBlock]:

    class FakeProcessActionsBlock:

        def __init__(
            self,
            fake_response_status: OperationStatusEnum = OperationStatusEnum.COMPLETED,
        ):
            self.response_status = fake_response_status

        def run(
            self, payment_method: protocols.AbstractPaymentMethod, *args: Sequence, **kwargs: dict
        ) -> protocols.AbstractBlockResponse:
            return domain.BlockResponse(status=self.response_status)

    assert issubclass(FakeProcessActionsBlock, protocols.AbstractBlock)
    return FakeProcessActionsBlock
