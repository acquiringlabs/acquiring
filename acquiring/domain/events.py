from dataclasses import dataclass
from typing import TYPE_CHECKING
from uuid import UUID

if TYPE_CHECKING:
    from acquiring.enums import OperationStatusEnum


@dataclass
class BlockEvent:
    status: "OperationStatusEnum"
    payment_method_id: UUID
    block_name: str

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}:{self.block_name}|{self.status}"

    class DoesNotExist(Exception):
        pass

    class DuplicateError(Exception):
        pass
