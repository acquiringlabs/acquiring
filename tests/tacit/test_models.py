from django_acquiring.events.models import BlockEventStatusChoices
from django_acquiring.payments.models import PaymentOperationStatusChoices, PaymentOperationTypeChoices
from django_acquiring.protocols.payments import PaymentOperationStatusEnum, PaymentOperationTypeEnum


# TODO Figure out a way to ensure that these two enums match at compile time/initialization time
def test_PaymentOperationTypeChoices_match_PaymentOperationTypeEnum():
    choices = set(member.value for member in PaymentOperationTypeChoices)
    enums = set(item.value for item in PaymentOperationTypeEnum)

    assert choices == enums


def test_PaymentOperationStatusChoices_match_PaymentOperationStatusEnum():
    choices = set(member.value for member in PaymentOperationStatusChoices)
    enums = set(item.value for item in PaymentOperationStatusEnum)

    assert choices == enums


def test_BlockEventStatusChoices_match_PaymentOperationStatusEnum():
    choices = set(member.value for member in BlockEventStatusChoices)
    enums = set(item.value for item in PaymentOperationStatusEnum)

    assert choices == enums
