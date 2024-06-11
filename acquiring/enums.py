"""An enumeration:

    is a set of symbolic names (members) bound to unique values

    can be iterated over to return its canonical (i.e. non-alias) members in definition order

    uses call syntax to return members by value

    uses index syntax to return members by name
"""

from enum import StrEnum


class OperationTypeEnum(StrEnum):
    """
    Payment operations is an umbrella term that refers to the entire lifecycle of money movement for a company.

    This definition is consistent with Modern Treasury glossary of terms
    See https://www.moderntreasury.com/learn/payment-operations
    """

    INITIALIZE = "initialize"
    PROCESS_ACTION = "process_action"

    PAY = "pay"
    CONFIRM = "confirm"

    VOID = "void"
    REFUND = "refund"

    AFTER_PAY = "after_pay"
    AFTER_CONFIRM = "after_confirm"
    AFTER_VOID = "after_void"
    AFTER_REFUND = "after_refund"


# TODO Create a better division of status, some OperationTypes cannot be defined with all of them.
# TODO For example, started cannot be the status of a BlockResponse
# TODO Or OperationResponse cannot have status NOT_PERFORMED when the operation type is pay.
# TODO Preserve that knowledge in the type system
class OperationStatusEnum(StrEnum):
    """
    Stacked Payment Operations have different statuses
    that are used in combination with the type of Payment Operation
    to allow or prevent a PaymentMethod into a decision logic function.
    """

    STARTED = "started"
    FAILED = "failed"
    COMPLETED = "completed"
    REQUIRES_ACTION = "requires_action"
    PENDING = "pending"  # awaiting action or a decision from the provider. See https://thecontentauthority.com/blog/processing-vs-pending
    NOT_PERFORMED = "not_performed"


class AtemptStatusEnum(StrEnum):
    """Possible statuses in which a PaymentAttempt may be, based on the PaymentOperations of its PaymentMethods"""

    REQUIRES_PAYMENT_METHOD = "requires_payment_method"  # also functions as "failed", which allows for retries.
    SUCCEEDED = "succeeded"
    PROCESSING = "processing"  # being worked on or under review.

    REQUIRES_ACTION = "requires_action"
    REQUIRES_CONFIRMATION = "requires_confirmation"

    CANCELED = "canceled"
