from django_acquiring.events import models as events_models
from django_acquiring.payments import models as payments_models
from django_acquiring.protocols.enums import OperationStatusEnum, OperationTypeEnum


# TODO Figure out a way to ensure that these two enums match at compile time/initialization time
def test_PaymentOperationTypeChoices_match_OperationTypeEnum():
    choices = set(member.value for member in payments_models.PaymentOperationTypeChoices)
    enums = set(item.value for item in OperationTypeEnum)

    assert choices == enums


def test_PaymentOperationStatusChoices_match_OperationStatusEnum():
    choices = set(member.value for member in payments_models.PaymentOperationStatusChoices)
    enums = set(item.value for item in OperationStatusEnum)

    assert choices == enums


def test_BlockEventStatusChoices_match_OperationStatusEnum():
    choices = set(member.value for member in events_models.BlockEventStatusChoices)
    enums = set(item.value for item in OperationStatusEnum)

    assert choices == enums


# TODO Figure out a way to ensure that there are no import specific objects, but instead it's always import modules
