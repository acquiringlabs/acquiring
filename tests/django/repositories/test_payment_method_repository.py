import uuid
from datetime import datetime, timedelta
from typing import Callable

import pytest
from faker import Faker

from acquiring import enums
from acquiring.utils import is_django_installed
from tests.django.utils import skip_if_django_not_installed

fake = Faker()

if is_django_installed():
    from django.utils import timezone  # TODO replace with native aware Python datetime object

    from acquiring import domain, models, repositories
    from tests.django.factories import (
        PaymentAttemptFactory,
        PaymentMethodFactory,
        PaymentOperationFactory,
        TokenFactory,
    )


@skip_if_django_not_installed
@pytest.mark.django_db
def test_givenCorrectData_whenCallingRepositoryAdd_thenPaymentMethodGetsCreated(
    django_assert_num_queries: Callable,
) -> None:

    payment_attempt = PaymentAttemptFactory()
    data = domain.DraftPaymentMethod(
        payment_attempt=payment_attempt.to_domain(),
        confirmable=True,
    )

    with django_assert_num_queries(7):
        result = repositories.django.PaymentMethodRepository().add(data)

    db_payment_methods = models.PaymentMethod.objects.all()
    assert len(db_payment_methods) == 1
    db_payment_method = db_payment_methods[0]

    assert db_payment_method.id == result.id
    assert db_payment_method.created_at == result.created_at
    assert db_payment_method.to_domain() == result


@skip_if_django_not_installed
@pytest.mark.django_db
@pytest.mark.parametrize("confirmable", [True, False])
def test_givenTokenData_whenCallingRepositoryAdd_thenTokenGetsCreated(
    django_assert_num_queries: Callable, confirmable: bool
) -> None:

    payment_attempt = PaymentAttemptFactory()
    data = domain.DraftPaymentMethod(
        payment_attempt=payment_attempt.to_domain(),
        confirmable=confirmable,
        token=domain.Token(
            created_at=timezone.now(),
            token=fake.sha256(raw_output=False),
            expires_at=timezone.now() + timedelta(days=365),
            fingerprint=fake.sha256(),
            metadata={"customer_id": str(uuid.uuid4())},
        ),
    )

    with django_assert_num_queries(8):
        result = repositories.django.PaymentMethodRepository().add(data)

    db_tokens = models.Token.objects.all()
    assert len(db_tokens) == 1
    db_token = db_tokens[0]

    db_payment_methods = models.PaymentMethod.objects.all()
    assert len(db_payment_methods) == 1
    db_payment_method = db_payment_methods[0]

    assert db_token.payment_method == db_payment_method

    assert result.token == db_token.to_domain()


@skip_if_django_not_installed
@pytest.mark.django_db
def test_givenExistingPaymentMethodRow_whenCallingRepositoryGet_thenPaymentGetsRetrieved(
    django_assert_num_queries: Callable,
) -> None:
    db_payment_attempt = PaymentAttemptFactory()
    db_payment_method = PaymentMethodFactory(payment_attempt=db_payment_attempt)
    db_token = TokenFactory(
        token=fake.sha256(),
        created_at=timezone.now(),
    )
    db_payment_method.token = db_token
    db_payment_method.save()
    PaymentOperationFactory.create(
        payment_method_id=db_payment_method.id,
        status=enums.OperationStatusEnum.STARTED,
        type=enums.OperationTypeEnum.INITIALIZE,
    )
    PaymentOperationFactory.create(
        payment_method_id=db_payment_method.id,
        status=enums.OperationStatusEnum.COMPLETED,
        type=enums.OperationTypeEnum.INITIALIZE,
    )

    with django_assert_num_queries(4):
        result = repositories.django.PaymentMethodRepository().get(id=db_payment_method.id)

    assert result == db_payment_method.to_domain()


@skip_if_django_not_installed
@pytest.mark.django_db
def test_givenNonExistingPaymentMethodRow_whenCallingRepositoryGet_thenDoesNotExistGetsRaise(
    django_assert_num_queries: Callable,
) -> None:
    payment_attempt = domain.PaymentAttempt(
        id=uuid.uuid4(),
        created_at=datetime.now(),
        amount=10,
        currency="USD",
        payment_method_ids=[],
    )

    payment_method = domain.PaymentMethod(
        id=uuid.uuid4(),
        payment_attempt=payment_attempt,
        created_at=datetime.now(),
        confirmable=False,
    )

    with django_assert_num_queries(2), pytest.raises(domain.PaymentMethod.DoesNotExist):
        repositories.django.PaymentMethodRepository().get(id=payment_method.id)


@skip_if_django_not_installed
@pytest.mark.django_db
def test_givenCorrectTokenDataAndExistingPaymentMethod_whenCallingRepositoryAddToken_thenTokenGetsCreated(
    django_assert_num_queries: Callable,
) -> None:

    db_payment_attempt = PaymentAttemptFactory()
    db_payment_method = PaymentMethodFactory(payment_attempt_id=db_payment_attempt.id)
    payment_method = db_payment_method.to_domain()
    token = domain.Token(created_at=timezone.now(), token=fake.sha256())

    with django_assert_num_queries(5):
        result = repositories.django.PaymentMethodRepository().add_token(
            payment_method=payment_method,
            token=token,
        )

    db_tokens = models.Token.objects.all()
    assert len(db_tokens) == 1
    db_token = db_tokens[0]

    assert db_token.to_domain() == token
    assert payment_method.token == token

    assert result == payment_method


# TODO Turn pytest.mark.django_db into skip if when pytest-django is not installed
@skip_if_django_not_installed
@pytest.mark.django_db
def test_givenNonExistingPaymentMethodRow_whenCallingRepositoryAddToken_thenDoesNotExistGetsRaise(
    django_assert_num_queries: Callable,
) -> None:

    payment_attempt = domain.PaymentAttempt(
        id=uuid.uuid4(),
        created_at=datetime.now(),
        amount=10,
        currency="USD",
        payment_method_ids=[],
    )

    payment_method = domain.PaymentMethod(
        id=uuid.uuid4(),
        payment_attempt=payment_attempt,
        created_at=datetime.now(),
        confirmable=False,
    )
    token = domain.Token(created_at=timezone.now(), token=fake.sha256())

    with django_assert_num_queries(2), pytest.raises(domain.PaymentMethod.DoesNotExist):
        repositories.django.PaymentMethodRepository().add_token(
            payment_method=payment_method,
            token=token,
        )
