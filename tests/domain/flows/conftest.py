from typing import Callable, Sequence, Type

import pytest

from acquiring import domain, protocols
from acquiring.enums import OperationStatusEnum


# TODO Define these two to accept block_event_repository as an optional argument


@pytest.fixture(scope="module")
def fake_block(  # type:ignore[misc]
    fake_block_event_repository: Callable[..., protocols.AbstractRepository]
) -> Type[protocols.AbstractBlock]:
    class FakeBlock:
        block_event_repository: protocols.AbstractRepository = fake_block_event_repository()

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

    return FakeBlock


@pytest.fixture(scope="module")
def fake_process_action_block(  # type:ignore[misc]
    fake_block_event_repository: Callable[..., protocols.AbstractRepository]
) -> Type[protocols.AbstractBlock]:

    class FakeProcessActionsBlock:
        block_event_repository: protocols.AbstractRepository = fake_block_event_repository()

        def __init__(
            self,
            fake_response_status: OperationStatusEnum = OperationStatusEnum.COMPLETED,
        ):
            self.response_status = fake_response_status

        def run(
            self, payment_method: protocols.AbstractPaymentMethod, *args: Sequence, **kwargs: dict
        ) -> protocols.AbstractBlockResponse:
            return domain.BlockResponse(status=self.response_status)

    return FakeProcessActionsBlock
