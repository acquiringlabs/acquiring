import functools
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Callable, Optional

from django_acquiring import domain
from django_acquiring.protocols.enums import OperationStatusEnum

if TYPE_CHECKING:
    from django_acquiring.protocols.flows import AbstractBlockResponse
    from django_acquiring.protocols.payments import AbstractPaymentMethod


@dataclass
class BlockResponse:
    status: OperationStatusEnum
    payment_method: "AbstractPaymentMethod"
    actions: list[dict] = field(default_factory=list)
    error_message: Optional[str] = None


def wrapped_by_block_events(function: Callable[[], "AbstractBlockResponse"]) -> Callable:
    """
    This decorator ensures that the starting and finishing block events get created.
    """
    from django_acquiring.repositories import BlockEventRepository

    repository = BlockEventRepository()

    @functools.wraps(function)
    def wrapper(*args, **kwargs) -> "AbstractBlockResponse":  # type: ignore[no-untyped-def]
        block_name = args[0].__class__.__name__
        payment_method = kwargs["payment_method"]

        repository.add(
            block_event=domain.BlockEvent(
                status=OperationStatusEnum.started,
                payment_method_id=payment_method.id,
                block_name=block_name,
            )
        )

        result = function(*args, **kwargs)

        repository.add(
            block_event=domain.BlockEvent(
                status=result.status,
                payment_method_id=payment_method.id,
                block_name=block_name,
            )
        )
        return result

    return wrapper
