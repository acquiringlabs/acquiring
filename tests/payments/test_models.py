from django_acquiring.payments.models import StageEventNameChoices, StageEventStatusChoices
from django_acquiring.payments.protocols import StageNameEnum, StageStatusEnum


# TODO Figure out a way to ensure that these two enums match at compile time/initialization time
def test_stageEventNameChoices_match_stageNameEnum():
    choices = set(member.value for member in StageEventNameChoices)
    enums = set(item.value for item in StageNameEnum)

    assert choices == enums


def test_stageEventStatusChoices_match_stageEventStatusEnum():
    choices = set(member.value for member in StageEventStatusChoices)
    enums = set(item.value for item in StageStatusEnum)

    assert choices == enums
