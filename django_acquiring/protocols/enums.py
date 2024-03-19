from enum import StrEnum


class OperationTypeEnum(StrEnum):
    initialize = "initialize"
    process_actions = "process_actions"

    pay = "pay"
    confirm = "confirm"

    refund = "refund"

    after_pay = "after_pay"
    after_confirm = "after_confirm"
    after_refund = "after_refund"


class OperationStatusEnum(StrEnum):
    started = "started"
    failed = "failed"
    completed = "completed"
    requires_action = "requires_action"
    pending = "pending"
