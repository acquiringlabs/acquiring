from typing import Callable

import pytest
from django.utils import timezone
from faker import Faker

from django_acquiring import domain, models, repositories
from tests.repositories.factories import PaymentAttemptFactory, PaymentMethodFactory

fake = Faker()


@pytest.mark.django_db
def test_givenCorrectData_whenCallingRepositoryAdd_thenPaymentOperationGetsCreated(
    django_assert_num_queries: Callable,
) -> None:
    db_payment_attempt = PaymentAttemptFactory()
    db_payment_method = PaymentMethodFactory(payment_attempt_id=db_payment_attempt.id)
    transaction = domain.Transaction(
        external_id=fake.uuid4(),
        timestamp=timezone.now(),
        provider_name=fake.company(),
        payment_method_id=db_payment_method.id,
        raw_data={},
    )

    with django_assert_num_queries(1):
        repositories.TransactionRepository().add(
            transaction=transaction,
        )

    assert models.Transaction.objects.count() == 1
    db_transaction = models.Transaction.objects.first()

    assert transaction == db_transaction.to_domain()
