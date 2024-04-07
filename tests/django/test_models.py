"""TODO Figure out a way to ensure that these two enums match at compile time/initialization time"""

from acquiring.utils import is_django_installed
from tests.django.utils import skip_if_django_not_installed

if is_django_installed():
    from acquiring import enums, models


@skip_if_django_not_installed
def test_PaymentOperationTypeChoices_match_OperationTypeEnum() -> None:
    choices = set(
        member.value for member in models.django.PaymentOperationTypeChoices  # type:ignore[attr-defined]
    )
    type_enums = set(item.value for item in enums.OperationTypeEnum)

    assert choices == type_enums


@skip_if_django_not_installed
def test_StatusChoices_match_OperationStatusEnum() -> None:
    choices = set(
        member.value for member in models.django.StatusChoices  # type:ignore[attr-defined]
    )
    status_enums = set(item.value for item in enums.OperationStatusEnum)

    assert choices == status_enums
