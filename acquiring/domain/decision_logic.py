import deal

from acquiring import enums, protocols

# TODO Test these functions with hypothesis


@deal.pure
def can_initialize(payment_method: "protocols.PaymentMethod") -> bool:
    """
    Return whether the payment_method can go through the initialize operation.
    """
    if payment_method.has_payment_operation(
        type=enums.OperationTypeEnum.INITIALIZE, status=enums.OperationStatusEnum.STARTED
    ):
        return False

    return True


@deal.pure
def can_process_action(payment_method: "protocols.PaymentMethod") -> bool:
    """
    Return whether the payment_method can go through the process_action operation.
    """
    if payment_method.has_payment_operation(
        type=enums.OperationTypeEnum.PROCESS_ACTION,
        status=enums.OperationStatusEnum.STARTED,
    ):
        return False

    if not (
        payment_method.has_payment_operation(
            type=enums.OperationTypeEnum.INITIALIZE,
            status=enums.OperationStatusEnum.STARTED,
        )
        and payment_method.has_payment_operation(
            type=enums.OperationTypeEnum.INITIALIZE,
            status=enums.OperationStatusEnum.REQUIRES_ACTION,
        )
    ):
        return False

    return True


@deal.pure
def can_after_pay(payment_method: "protocols.PaymentMethod") -> bool:
    """
    Return whether the payment_method can go through the after pay operation.
    """
    if payment_method.has_payment_operation(
        type=enums.OperationTypeEnum.AFTER_PAY,
        status=enums.OperationStatusEnum.STARTED,
    ):
        return False

    if any([can_initialize(payment_method), can_process_action(payment_method)]):
        return False

    if payment_method.has_payment_operation(
        type=enums.OperationTypeEnum.INITIALIZE,
        status=enums.OperationStatusEnum.STARTED,
    ):
        if payment_method.has_payment_operation(
            type=enums.OperationTypeEnum.INITIALIZE,
            status=enums.OperationStatusEnum.REQUIRES_ACTION,
        ) and not payment_method.has_payment_operation(
            type=enums.OperationTypeEnum.PROCESS_ACTION,
            status=enums.OperationStatusEnum.COMPLETED,
        ):
            return False
        elif not payment_method.has_payment_operation(
            type=enums.OperationTypeEnum.INITIALIZE,
            status=enums.OperationStatusEnum.REQUIRES_ACTION,
        ) and not any(
            [
                payment_method.has_payment_operation(
                    type=enums.OperationTypeEnum.INITIALIZE,
                    status=enums.OperationStatusEnum.COMPLETED,
                ),
                payment_method.has_payment_operation(
                    type=enums.OperationTypeEnum.INITIALIZE,
                    status=enums.OperationStatusEnum.NOT_PERFORMED,
                ),
            ]
        ):
            return False

    if payment_method.has_payment_operation(
        type=enums.OperationTypeEnum.PAY,
        status=enums.OperationStatusEnum.STARTED,
    ) and not payment_method.has_payment_operation(
        type=enums.OperationTypeEnum.PAY,
        status=enums.OperationStatusEnum.COMPLETED,
    ):
        return False

    if payment_method.has_payment_operation(
        type=enums.OperationTypeEnum.PAY,
        status=enums.OperationStatusEnum.STARTED,
    ) and not payment_method.has_payment_operation(
        type=enums.OperationTypeEnum.PAY,
        status=enums.OperationStatusEnum.COMPLETED,
    ):
        return False

    return True


@deal.pure
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
        type=enums.OperationTypeEnum.AFTER_PAY,
        status=enums.OperationStatusEnum.COMPLETED,
    ):
        return False

    if payment_method.has_payment_operation(
        type=enums.OperationTypeEnum.CONFIRM,
        status=enums.OperationStatusEnum.STARTED,
    ):
        return False

    return True


@deal.pure
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
                type=enums.OperationTypeEnum.INITIALIZE,
                status=enums.OperationStatusEnum.COMPLETED,
            ),
            payment_method.has_payment_operation(
                type=enums.OperationTypeEnum.INITIALIZE,
                status=enums.OperationStatusEnum.NOT_PERFORMED,
            ),
        ]
    ):
        return False

    if payment_method.has_payment_operation(
        type=enums.OperationTypeEnum.INITIALIZE,
        status=enums.OperationStatusEnum.REQUIRES_ACTION,
    ) and not payment_method.has_payment_operation(
        type=enums.OperationTypeEnum.PROCESS_ACTION,
        status=enums.OperationStatusEnum.COMPLETED,
    ):
        return False

    if not payment_method.has_payment_operation(
        type=enums.OperationTypeEnum.PAY,
        status=enums.OperationStatusEnum.COMPLETED,
    ):
        return False

    if not payment_method.has_payment_operation(
        type=enums.OperationTypeEnum.AFTER_PAY,
        status=enums.OperationStatusEnum.COMPLETED,
    ):
        return False

    if not payment_method.has_payment_operation(
        type=enums.OperationTypeEnum.CONFIRM,
        status=enums.OperationStatusEnum.COMPLETED,
    ):
        return False

    if payment_method.has_payment_operation(
        type=enums.OperationTypeEnum.AFTER_CONFIRM,
        status=enums.OperationStatusEnum.STARTED,
    ):
        return False

    return True


@deal.pure
def can_refund(payment_method: "protocols.PaymentMethod") -> bool:
    """
    Return whether the payment_method can go through the refund operation.
    """
    if any(
        [
            can_initialize(payment_method),
            can_process_action(payment_method),
            can_after_pay(payment_method),
            can_confirm(payment_method),
            can_after_confirm(payment_method),
        ]
    ):
        return False

    if not payment_method.has_payment_operation(
        type=enums.OperationTypeEnum.AFTER_PAY,
        status=enums.OperationStatusEnum.COMPLETED,
    ):
        return False

    if payment_method.confirmable and not payment_method.has_payment_operation(
        type=enums.OperationTypeEnum.AFTER_CONFIRM,
        status=enums.OperationStatusEnum.COMPLETED,
    ):
        return False

    if payment_method.count_payment_operation(
        type=enums.OperationTypeEnum.REFUND,
        status=enums.OperationStatusEnum.STARTED,
    ) > payment_method.count_payment_operation(
        type=enums.OperationTypeEnum.REFUND,
        status=enums.OperationStatusEnum.COMPLETED,
    ):
        return False

    return True
