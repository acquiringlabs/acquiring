from uuid import UUID

from django_acquiring.events import models
from django_acquiring.protocols import events


class BlockEventRepository:
    def add(self, block_event: events.AbstractBlockEvent) -> events.AbstractBlockEvent:
        block_event = models.BlockEvent(
            status=block_event.status,
            payment_method_id=block_event.payment_method_id,
            block_name=block_event.block_name,
        )
        block_event.save()
        return block_event.to_domain()

    def get(self, id: UUID) -> events.AbstractBlockEvent: ...  # type: ignore[empty-body]
