from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
import deal

from acquiring import enums, protocols


@dataclass
class PaymentMethod:
    """Represents how a PaymentAttempt gets paid"""

    id: protocols.ExistingPaymentMethodId
    created_at: datetime
    payment_attempt_id: protocols.ExistingPaymentAttemptId
    confirmable: bool
    tokens: list["protocols.Token"] = field(default_factory=list)
    operation_events: list["protocols.OperationEvent"] = field(default_factory=list)

    def __repr__(self) -> str:
        """String representation of the class"""
        return f"{self.__class__.__name__}:{self.id}"

    @deal.pure
    def has_operation_event(self, type: "enums.OperationTypeEnum", status: "enums.OperationStatusEnum") -> bool:
        """Returns True if there is a OperationEvent associated with this PaymentMethod of given type and status"""
        return any(operation.type == type and operation.status == status for operation in self.operation_events)

    @deal.pure
    @deal.post(lambda result: result >= 0)
    def count_operation_event(self, type: "enums.OperationTypeEnum", status: "enums.OperationStatusEnum") -> int:
        """Returns the number of OperationEvents associated with this PaymentMethod of given type and status"""
        return sum(1 for operation in self.operation_events if operation.type == type and operation.status == status)

    class DoesNotExist(Exception):
        """
        This exception gets raised when the database representation could not be found.

        Most often, you'll see this raised when a database NotFound exception is raised on a Repository class
        """

        pass


@dataclass
class DraftPaymentMethod:
    """Parses the data needed to create a PaymentMethod via its Repository"""

    payment_attempt_id: protocols.ExistingPaymentAttemptId
    confirmable: bool
    tokens: list["protocols.DraftToken"] = field(default_factory=list)


@dataclass
class Token:
    timestamp: datetime
    token: str
    payment_method_id: protocols.ExistingPaymentMethodId
    metadata: Optional[dict[str, str | int]] = field(default_factory=dict)
    expires_at: Optional[datetime] = None
    fingerprint: Optional[str] = None

    class DoesNotExist(Exception):
        """
        This exception gets raised when the database representation could not be found.

        Most often, you'll see this raised when a database NotFound exception is raised on a Repository class
        """

        pass

    def __repr__(self) -> str:
        """String representation of the class"""
        return f"{self.__class__.__name__}:{self.token}"


@dataclass
class DraftToken:
    """
    Dataclass passed as an argument to Token repository in order to create an instance of Token.

    Unlike an actual Token, no payment_method_id attribute is specified.

    This separation ensures that we don't have to check for Optional attributes in a dataclass
    shared both as the input and the output of the Repository.add method.
    """

    timestamp: datetime
    token: str
    metadata: Optional[dict[str, str | int]] = field(default_factory=dict)
    expires_at: Optional[datetime] = None
    fingerprint: Optional[str] = None

    def __repr__(self) -> str:
        """String representation of the class"""
        return f"{self.__class__.__name__}:{self.token}"
