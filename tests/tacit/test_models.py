from django_acquiring import enums, models


# TODO Figure out a way to ensure that these two enums match at compile time/initialization time
def test_PaymentOperationTypeChoices_match_OperationTypeEnum() -> None:
    choices = set(
        member.value for member in models.django.PaymentOperationTypeChoices  # type:ignore[attr-defined]
    )
    type_enums = set(item.value for item in enums.OperationTypeEnum)

    assert choices == type_enums


def test_StatusChoices_match_OperationStatusEnum() -> None:
    choices = set(
        member.value for member in models.django.StatusChoices  # type:ignore[attr-defined]
    )
    status_enums = set(item.value for item in enums.OperationStatusEnum)

    assert choices == status_enums
