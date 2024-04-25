import functools
from dataclasses import dataclass, field
from typing import Callable, Optional, Sequence

from acquiring import domain, protocols
from acquiring.enums import OperationStatusEnum


@dataclass
class BlockResponse:
    status: OperationStatusEnum
    actions: list[dict] = field(default_factory=list)
    error_message: Optional[str] = None


def wrapped_by_block_events(  # type:ignore[misc]
    function: Callable[..., "protocols.BlockResponse"]
) -> Callable[..., "protocols.BlockResponse"]:
    """
    This decorator ensures that the starting and finishing block events get created.
    """

    @functools.wraps(function)
    def wrapper(
        self: "protocols.Block",
        payment_method: "protocols.PaymentMethod",
        *args: Sequence,
        **kwargs: dict,
    ) -> "protocols.BlockResponse":
        block_name = self.__class__.__name__

        self.block_event_repository.add(
            block_event=domain.BlockEvent(
                status=OperationStatusEnum.STARTED,
                payment_method_id=payment_method.id,
                block_name=block_name,
            )
        )

        result = function(self, payment_method, *args, **kwargs)

        self.block_event_repository.add(
            block_event=domain.BlockEvent(
                status=result.status,
                payment_method_id=payment_method.id,
                block_name=block_name,
            )
        )
        return result

    return wrapper
