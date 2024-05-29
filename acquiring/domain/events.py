from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from acquiring.enums import OperationStatusEnum


@dataclass(frozen=True)
class BlockEvent:
    """
    Represents a wide event related to executing the code inside a Block class.
    """

    created_at: datetime
    status: "OperationStatusEnum"
    payment_method_id: UUID
    block_name: str

    def __repr__(self) -> str:
        """String representation of the class"""
        return f"{self.__class__.__name__}:{self.block_name}|{self.status}"

    class DoesNotExist(Exception):
        """
        This exception gets raised when the database representation could not be found.

        Most often, you'll see this raised when a database NotFound exception is raised on a Repository class
        """

        pass

    class Duplicated(Exception):
        """This exception gets raised as a result of an Integrity error that has to do with a UNIQUE constraint"""

        pass
