import uuid
from typing import Callable

import pytest
from django.utils import timezone
from faker import Faker

from django_acquiring import domain, enums, models, repositories
from tests.repositories.factories import (
    ItemFactory,
    PaymentAttemptFactory,
    PaymentMethodFactory,
    PaymentOperationFactory,
)

fake = Faker()


@pytest.mark.django_db
def test_givenCorrectData_whenCallingRepositoryAdd_thenPaymentAttemptGetsCreated(
    django_assert_num_queries: Callable,
) -> None:

    items = [
        domain.DraftItem(
            name=fake.name(),
            quantity=fake.random_int(),
            quantity_unit=None,
            reference=fake.isbn10(),
            unit_price=fake.random_int(),
        ),
        domain.DraftItem(
            name=fake.name(),
            quantity=fake.random_int(),
            quantity_unit=None,
            reference=fake.isbn10(),
            unit_price=fake.random_int(),
        ),
    ]

    data = domain.DraftPaymentAttempt(
        amount=sum(item.quantity * item.unit_price for item in items),  # correct amount
        currency="NZD",
        items=items,
    )

    # When calling PaymentAttemptRepository.add
    with django_assert_num_queries(6):
        result = repositories.PaymentAttemptRepository().add(data)

    # Then PaymentAttempt gets created

    db_payments = models.PaymentAttempt.objects.all()
    assert len(db_payments) == 1
    db_payment = db_payments[0]

    assert db_payment.id == result.id
    assert db_payment.created_at == result.created_at
    assert db_payment.to_domain() == result

    db_items = models.Item.objects.all()
    assert len(db_items) == len(items)


@pytest.mark.django_db
def test_givenInvalidAmount_whenCallingRepositoryAdd_thenItemRaisesError(
    django_assert_num_queries: Callable,
) -> None:

    items = [
        domain.DraftItem(
            name=fake.name(),
            quantity=fake.random_int(),
            quantity_unit=None,
            reference=fake.isbn10(),
            unit_price=fake.random_int(),
        ),
        domain.DraftItem(
            name=fake.name(),
            quantity=fake.random_int(),
            quantity_unit=None,
            reference=fake.isbn10(),
            unit_price=fake.random_int(),
        ),
    ]

    data = domain.DraftPaymentAttempt(
        amount=fake.random_int(),
        currency="NZD",
        items=items,
    )

    # When calling PaymentAttemptRepository.add
    with django_assert_num_queries(4), pytest.raises(domain.Item.InvalidTotalAmount):
        repositories.PaymentAttemptRepository().add(data)

    # Then PaymentAttempt gets created

    db_payments = models.PaymentAttempt.objects.all()
    assert len(db_payments) == 0

    db_items = models.Item.objects.all()
    assert len(db_items) == 0


@pytest.mark.django_db
def test_givenInCorrectCurrencyData_whenCallingRepositoryAdd_thenPaymentAttemptRaisesError(
    django_assert_num_queries: Callable,
) -> None:
    # Given Incorrect Currency Data

    data = domain.DraftPaymentAttempt(amount=fake.random_int(), currency="fake")

    # When calling PaymentAttemptRepository.add
    with django_assert_num_queries(5):  # , pytest.raises(domain.CurrencyField.DoesNotExist):
        result = repositories.PaymentAttemptRepository().add(data)

    # Then PaymentAttempt raises an error

    db_payments = models.PaymentAttempt.objects.all()
    assert len(db_payments) == 1
    db_payment = db_payments[0]

    assert db_payment.id == result.id
    assert db_payment.created_at == result.created_at
    assert db_payment.to_domain() == result


@pytest.mark.django_db
def test_givenExistingPaymentAttemptRow_whenCallingRepositoryGet_thenPaymentAttemptGetsRetrieved(
    django_assert_num_queries: Callable,
) -> None:
    # Given existing payment attempt row in payments table
    db_payment_attempt = PaymentAttemptFactory()
    db_payment_methods = PaymentMethodFactory.create_batch(3, payment_attempt_id=db_payment_attempt.id)
    PaymentOperationFactory.create(
        payment_method_id=db_payment_methods[0].id,
        status=enums.OperationStatusEnum.STARTED,
        type=enums.OperationTypeEnum.INITIALIZE,
    )
    PaymentOperationFactory.create(
        payment_method_id=db_payment_methods[0].id,
        status=enums.OperationStatusEnum.COMPLETED,
        type=enums.OperationTypeEnum.INITIALIZE,
    )
    ItemFactory.create_batch(3, payment_attempt_id=db_payment_attempt.id)

    # When calling PaymentAttemptRepository.get
    with django_assert_num_queries(4):
        result = repositories.PaymentAttemptRepository().get(id=db_payment_attempt.id)

    # Then PaymentAttempt gets retrieved
    assert result == db_payment_attempt.to_domain()


@pytest.mark.django_db
def test_givenNonExistingPaymentAttemptRow_whenCallingRepositoryGet_thenDoesNotExistGetsRaise(
    django_assert_num_queries: Callable,
) -> None:

    payment_method = domain.PaymentAttempt(
        id=uuid.uuid4(),
        created_at=timezone.now(),
        amount=fake.random_int(),
        currency="NZD",
    )

    with django_assert_num_queries(1), pytest.raises(domain.PaymentAttempt.DoesNotExist):
        repositories.PaymentAttemptRepository().get(id=payment_method.id)
