from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Sequence
from uuid import UUID

from acquiring import enums, protocols


# TODO PaymentAttempt must have status exposed
@dataclass
class PaymentAttempt:
    """
    From Old French atempter: "seek or try to do, make an effort to perform"
    See https://www.etymonline.com/word/attempt#etymonline_v_41850
    """

    id: protocols.ExistingPaymentAttemptId
    created_at: datetime
    amount: int
    currency: str
    payment_methods: list[protocols.PaymentMethod] = field(default_factory=list)
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


@dataclass(frozen=True)
class Milestone:
    """Checkpoints being created after a certain threshold on the lifecycle of a PaymentMethod is reached"""

    created_at: datetime
    type: "enums.MilestoneTypeEnum"
    payment_method_id: protocols.ExistingPaymentMethodId
    payment_attempt_id: protocols.ExistingPaymentAttemptId


@dataclass
class DraftPaymentAttempt:
    """
    Dataclass passed as an argument to PaymentAttempt repository in order to create an instance of PaymentAttempt.

    Unlike an actual PaymentAttempt, no id or created_at attributes are specified. They belong to already created
    instances.

    This separation ensures that we don't have to check for Optional attributes in a dataclass
    shared both as the input and the output of the Repository.add method.
    """

    amount: int
    currency: str
    items: Sequence["protocols.DraftItem"] = field(default_factory=list)


@dataclass
class Item:
    id: UUID
    created_at: datetime
    payment_attempt_id: protocols.ExistingPaymentAttemptId
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
