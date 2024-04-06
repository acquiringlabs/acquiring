import uuid
from dataclasses import dataclass

from typing import Callable, Optional

import pytest

from django_acquiring import domain, protocols


@pytest.fixture(scope="module")
def fake_block_event_repository() -> (
    Callable[[Optional[list[protocols.AbstractBlockEvent]]], protocols.AbstractRepository]
):

    @dataclass
    class FakeBlockEventRepository:
        units: list[protocols.AbstractBlockEvent]

        def add(self, block_event: protocols.AbstractBlockEvent) -> protocols.AbstractBlockEvent:
            block_event = domain.BlockEvent(
                status=block_event.status,
                payment_method_id=block_event.payment_method_id,
                block_name=block_event.block_name,
            )
            self.units.append(block_event)
            return block_event

        def get(  # type:ignore[empty-body]
            self, id: uuid.UUID
        ) -> protocols.AbstractBlockEvent: ...

    assert issubclass(FakeBlockEventRepository, protocols.AbstractRepository)

    def build_repository(
        units: Optional[list[protocols.AbstractBlockEvent]] = None,
    ) -> protocols.AbstractRepository:
        return FakeBlockEventRepository(units=units if units else [])

    return build_repository
