from dataclasses import dataclass, field
from types import TracebackType
from typing import Callable, Optional, Self, Sequence

import pytest

from acquiring import domain, protocols
from acquiring.enums import OperationStatusEnum

# TODO Define these two to accept block_event_repository as an optional argument


@pytest.fixture(scope="module")
def fake_block(  # type:ignore[misc]
    fake_block_event_repository: Callable[..., protocols.Repository]
) -> type[protocols.Block]:
    class FakeBlock:
        block_event_repository: protocols.Repository = fake_block_event_repository()

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
            self, payment_method: protocols.PaymentMethod, *args: Sequence, **kwargs: dict
        ) -> protocols.BlockResponse:
            return domain.BlockResponse(
                status=self.response_status,
                actions=self.response_actions,
            )

    return FakeBlock


@pytest.fixture(scope="module")
def fake_process_action_block(  # type:ignore[misc]
    fake_block_event_repository: Callable[..., protocols.Repository]
) -> type[protocols.Block]:

    class FakeProcessActionsBlock:
        block_event_repository: protocols.Repository = fake_block_event_repository()

        def __init__(
            self,
            fake_response_status: OperationStatusEnum = OperationStatusEnum.COMPLETED,
        ):
            self.response_status = fake_response_status

        def run(
            self, payment_method: protocols.PaymentMethod, *args: Sequence, **kwargs: dict
        ) -> protocols.BlockResponse:
            return domain.BlockResponse(status=self.response_status)

    return FakeProcessActionsBlock


@pytest.fixture(scope="module")
def fake_unit_of_work() -> type[protocols.UnitOfWork]:

    @dataclass
    class FakeUnitOfWork:
        payment_method_repository_class: type[protocols.Repository]
        payment_methods: protocols.Repository = field(init=False)

        payment_operation_repository_class: type[protocols.Repository]
        payment_operations: protocols.Repository = field(init=False)

        def __enter__(self) -> Self:
            self.payment_methods = self.payment_method_repository_class()
            self.payment_operations = self.payment_operation_repository_class()
            return self

        def __exit__(
            self,
            exc_type: Optional[type[Exception]],
            exc_value: Optional[type[Exception]],
            exc_tb: Optional[TracebackType],
        ) -> None:
            pass

        def commit(self) -> None:
            pass

        def rollback(self) -> None:
            pass

    return FakeUnitOfWork
