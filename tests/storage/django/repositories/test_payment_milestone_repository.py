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
def test_givenCorrectData_whenCallingRepositoryAdd_thenPaymentMilestoneGetsCreated(
    type: enums.AtemptStatusEnum,
) -> None:

    db_payment_method = PaymentMethodFactory(payment_attempt_id=PaymentAttemptFactory().id)

    result = storage.django.PaymentMilestoneRepository().add(db_payment_method.to_domain(), type)

    db_payment_milestones = storage.django.models.PaymentMilestone.objects.all()
    assert len(db_payment_milestones) == 1
    db_payment_milestone = db_payment_milestones[0]

    assert db_payment_milestone.to_domain() == result
