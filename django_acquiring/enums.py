from enum import StrEnum


class OperationTypeEnum(StrEnum):
    INITIALIZE = "initialize"
    PROCESS_ACTION = "process_action"

    PAY = "pay"
    CONFIRM = "confirm"

    REFUND = "refund"

    AFTER_PAY = "after_pay"
    AFTER_CONFIRM = "after_confirm"
    AFTER_REFUND = "after_refund"


class OperationStatusEnum(StrEnum):
    STARTED = "started"
    FAILED = "failed"
    COMPLETED = "completed"
    REQUIRES_ACTION = "requires_action"
    PENDING = "pending"
    NOT_PERFORMED = "not_performed"
