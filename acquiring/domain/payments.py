from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Sequence
from uuid import UUID

from acquiring import enums, protocols


# TODO frozen=True compatible with protocols.PaymentOperation (expected settable variable, got read-only attribute)
@dataclass
class PaymentOperation:
    type: "enums.OperationTypeEnum"
    status: "enums.OperationStatusEnum"
    payment_method_id: UUID

    def __repr__(self) -> str:
        """String representation of the class"""
        return f"{self.__class__.__name__}:{self.type}|{self.status}"

    class Duplicated(Exception):
        """This exception gets raised as a result of an Integrity error that has to do with a UNIQUE constraint"""

        pass


@dataclass
class PaymentMethod:
    id: UUID
    created_at: datetime
    payment_attempt: "protocols.PaymentAttempt"
    confirmable: bool
    tokens: list["protocols.Token"] = field(default_factory=list)
    payment_operations: list["protocols.PaymentOperation"] = field(default_factory=list)

    def __repr__(self) -> str:
        """String representation of the class"""
        return f"{self.__class__.__name__}:{self.id}"

    def has_payment_operation(self, type: "enums.OperationTypeEnum", status: "enums.OperationStatusEnum") -> bool:
        return any(operation.type == type and operation.status == status for operation in self.payment_operations)

    class DoesNotExist(Exception):
        """
        This exception gets raised when the database representation could not be found.

        Most often, you'll see this raised when a database NotFound exception is raised on a Repository class
        """

        pass


@dataclass
class DraftPaymentMethod:
    payment_attempt: "protocols.PaymentAttempt"
    confirmable: bool
    tokens: list["protocols.DraftToken"] = field(default_factory=list)


@dataclass
class Item:
    id: UUID
    created_at: datetime
    payment_attempt_id: UUID
    reference: str
    name: str
    quantity: int
    quantity_unit: Optional[str]
    unit_price: int

    class InvalidTotalAmount(Exception):
        pass


@dataclass
class DraftItem:
    reference: str
    name: str
    quantity: int
    unit_price: int
    quantity_unit: Optional[str] = None


@dataclass
class PaymentAttempt:
    id: UUID
    created_at: datetime
    amount: int
    currency: str
    payment_method_ids: list[UUID] = field(default_factory=list)
    items: Sequence["protocols.Item"] = field(default_factory=list)

    def __repr__(self) -> str:
        """String representation of the class"""
        return f"{self.__class__.__name__}:{self.id}|{self.amount}{self.currency}"

    class DoesNotExist(Exception):
        """
        This exception gets raised when the database representation could not be found.

        Most often, you'll see this raised when a database NotFound exception is raised on a Repository class
        """

        pass


@dataclass
class DraftPaymentAttempt:
    amount: int
    currency: str
    items: Sequence["protocols.DraftItem"] = field(default_factory=list)


@dataclass
class DraftToken:
    created_at: datetime
    token: str
    metadata: Optional[dict[str, str | int]] = field(default_factory=dict)
    expires_at: Optional[datetime] = None
    fingerprint: Optional[str] = None

    def __repr__(self) -> str:
        """String representation of the class"""
        return f"{self.__class__.__name__}:{self.token}"


@dataclass
class Token:
    created_at: datetime
    token: str
    payment_method_id: UUID
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
