"""Events are Immutable dataclasses that record the occurrence of something interesting."""

from dataclasses import dataclass
from datetime import datetime
from acquiring import enums, protocols


@dataclass(frozen=True)
class BlockEvent:
    """
    Represents a wide event related to executing the code inside a Block class.
    """

    created_at: datetime
    status: "enums.OperationStatusEnum"
    payment_method_id: protocols.ExistingPaymentMethodId
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


@dataclass(frozen=True)
class OperationEvent:
    """Used to decide if the associated PaymentMethod can enter a given operation type in the PaymentMethodSaga"""

    created_at: datetime
    type: "enums.OperationTypeEnum"
    status: "enums.OperationStatusEnum"
    payment_method_id: protocols.ExistingPaymentMethodId

    def __repr__(self) -> str:
        """String representation of the class"""
        return f"{self.__class__.__name__}:{self.type}|{self.status}"


# TODO assert that all dataclasses defined in this file are immutable
