import pytest
from faker import Faker
from acquiring import enums
from acquiring.utils import is_django_installed
from tests.storage.utils import skip_if_django_not_installed

if is_django_installed():
    from acquiring import storage
    from tests.storage.django.factories import PaymentAttemptFactory, PaymentMethodFactory

fake = Faker()


@skip_if_django_not_installed
@pytest.mark.django_db
@pytest.mark.parametrize("type", enums.AtemptStatusEnum)
def test_givenCorrectData_whenCallingRepositoryAdd_thenMilestoneGetsCreated(
    type: enums.AtemptStatusEnum,
) -> None:

    db_payment_method = PaymentMethodFactory(payment_attempt_id=PaymentAttemptFactory().id)

    result = storage.django.MilestoneRepository().add(db_payment_method.to_domain(), type)

    db_milestones = storage.django.models.Milestone.objects.all()
    assert len(db_milestones) == 1
    db_milestone = db_milestones[0]

    assert db_milestone.to_domain() == result
