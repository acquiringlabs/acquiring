from acquiring import protocols
from acquiring.enums import OperationStatusEnum, OperationTypeEnum

# TODO Test these functions with hypothesis


def can_initialize(payment_method: "protocols.PaymentMethod") -> bool:
    """
    Return whether the payment_method can go through the initialize operation.
    """
    if payment_method.has_payment_operation(type=OperationTypeEnum.INITIALIZE, status=OperationStatusEnum.STARTED):
        return False

    return True


def can_process_action(payment_method: "protocols.PaymentMethod") -> bool:
    """
    Return whether the payment_method can go through the process_action operation.
    """
    if payment_method.has_payment_operation(
        type=OperationTypeEnum.PROCESS_ACTION,
        status=OperationStatusEnum.STARTED,
    ):
        return False

    if not (
        payment_method.has_payment_operation(
            type=OperationTypeEnum.INITIALIZE,
            status=OperationStatusEnum.STARTED,
        )
        and payment_method.has_payment_operation(
            type=OperationTypeEnum.INITIALIZE,
            status=OperationStatusEnum.REQUIRES_ACTION,
        )
    ):
        return False

    return True


def can_after_pay(payment_method: "protocols.PaymentMethod") -> bool:
    """
    Return whether the payment_method can go through the after pay operation.
    """
    if payment_method.has_payment_operation(
        type=OperationTypeEnum.AFTER_PAY,
        status=OperationStatusEnum.STARTED,
    ):
        return False

    if any([can_initialize(payment_method), can_process_action(payment_method)]):
        return False

    if payment_method.has_payment_operation(
        type=OperationTypeEnum.INITIALIZE,
        status=OperationStatusEnum.STARTED,
    ):
        if payment_method.has_payment_operation(
            type=OperationTypeEnum.INITIALIZE,
            status=OperationStatusEnum.REQUIRES_ACTION,
        ) and not payment_method.has_payment_operation(
            type=OperationTypeEnum.PROCESS_ACTION,
            status=OperationStatusEnum.COMPLETED,
        ):
            return False
        elif not payment_method.has_payment_operation(
            type=OperationTypeEnum.INITIALIZE,
            status=OperationStatusEnum.REQUIRES_ACTION,
        ) and not any(
            [
                payment_method.has_payment_operation(
                    type=OperationTypeEnum.INITIALIZE,
                    status=OperationStatusEnum.COMPLETED,
                ),
                payment_method.has_payment_operation(
                    type=OperationTypeEnum.INITIALIZE,
                    status=OperationStatusEnum.NOT_PERFORMED,
                ),
            ]
        ):
            return False

    if payment_method.has_payment_operation(
        type=OperationTypeEnum.PAY,
        status=OperationStatusEnum.STARTED,
    ) and not payment_method.has_payment_operation(
        type=OperationTypeEnum.PAY,
        status=OperationStatusEnum.COMPLETED,
    ):
        return False

    if payment_method.has_payment_operation(
        type=OperationTypeEnum.PAY,
        status=OperationStatusEnum.STARTED,
    ) and not payment_method.has_payment_operation(
        type=OperationTypeEnum.PAY,
        status=OperationStatusEnum.COMPLETED,
    ):
        return False

    return True


def can_confirm(payment_method: "protocols.PaymentMethod") -> bool:
    """
    Return whether the payment_method can go through the confirm operation.
    """
    if payment_method.confirmable is False:
        return False

    if any(
        [
            can_initialize(payment_method),
            can_process_action(payment_method),
            can_after_pay(payment_method),
        ]
    ):
        return False

    if not payment_method.has_payment_operation(
        type=OperationTypeEnum.AFTER_PAY,
        status=OperationStatusEnum.COMPLETED,
    ):
        return False

    if payment_method.has_payment_operation(
        type=OperationTypeEnum.CONFIRM,
        status=OperationStatusEnum.STARTED,
    ):
        return False

    return True


def can_after_confirm(payment_method: "protocols.PaymentMethod") -> bool:
    """
    Return whether the payment_method can go through the after confirm operation.
    """
    if any(
        [
            can_initialize(payment_method),
            can_process_action(payment_method),
            can_after_pay(payment_method),
            can_confirm(payment_method),
        ]
    ):
        return False

    if not payment_method.confirmable:
        return False

    if not any(
        [
            payment_method.has_payment_operation(
                type=OperationTypeEnum.INITIALIZE,
                status=OperationStatusEnum.COMPLETED,
            ),
            payment_method.has_payment_operation(
                type=OperationTypeEnum.INITIALIZE,
                status=OperationStatusEnum.NOT_PERFORMED,
            ),
        ]
    ):
        return False

    if payment_method.has_payment_operation(
        type=OperationTypeEnum.INITIALIZE,
        status=OperationStatusEnum.REQUIRES_ACTION,
    ) and not payment_method.has_payment_operation(
        type=OperationTypeEnum.PROCESS_ACTION,
        status=OperationStatusEnum.COMPLETED,
    ):
        return False

    if not payment_method.has_payment_operation(
        type=OperationTypeEnum.PAY,
        status=OperationStatusEnum.COMPLETED,
    ):
        return False

    if not payment_method.has_payment_operation(
        type=OperationTypeEnum.AFTER_PAY,
        status=OperationStatusEnum.COMPLETED,
    ):
        return False

    if not payment_method.has_payment_operation(
        type=OperationTypeEnum.CONFIRM,
        status=OperationStatusEnum.COMPLETED,
    ):
        return False

    if payment_method.has_payment_operation(
        type=OperationTypeEnum.AFTER_CONFIRM,
        status=OperationStatusEnum.STARTED,
    ):
        return False

    return True
