"""Blocks contains the functionality associated with the Block Layer of the domain"""

import functools
from dataclasses import dataclass, field
from datetime import datetime
from typing import Callable, Optional, Sequence

from acquiring import domain, protocols
from acquiring.enums import OperationStatusEnum


# TODO Can I separate a nonFailed from a Failed BlockResponse? (error message Optionality is code smell)
@dataclass
class BlockResponse:
    """
    Specifies the data meant to be the output of the Block.run method.
    """

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
        unit_of_work: "protocols.UnitOfWork",
        payment_method: "protocols.PaymentMethod",
        *args: Sequence,
        **kwargs: dict,
    ) -> "protocols.BlockResponse":
        """Wrapper meant to be called when method gets decorated with this function"""
        block_name = self.__class__.__name__

        with unit_of_work as uow:
            uow.block_events.add(
                block_event=domain.BlockEvent(
                    created_at=datetime.now(),
                    status=OperationStatusEnum.STARTED,
                    payment_method_id=payment_method.id,
                    block_name=block_name,
                )
            )
            uow.commit()

        result = function(self, unit_of_work, payment_method, *args, **kwargs)

        with unit_of_work as uow:
            uow.block_events.add(
                block_event=domain.BlockEvent(
                    created_at=datetime.now(),
                    status=result.status,
                    payment_method_id=payment_method.id,
                    block_name=block_name,
                )
            )
            uow.commit()
        return result

    return wrapper
