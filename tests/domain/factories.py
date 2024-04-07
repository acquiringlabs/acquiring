import random
from datetime import datetime

import factory
from faker import Faker

from acquiring import domain

fake = Faker()


class PaymentAttemptFactory(factory.Factory):
    id = factory.LazyAttribute(lambda _: fake.uuid4())
    created_at = factory.LazyAttribute(lambda _: datetime.now())
    currency = factory.LazyAttribute(lambda _: fake.currency_code())
    amount = factory.LazyAttribute(lambda _: random.randint(0, 999999))

    class Meta:
        model = domain.PaymentAttempt


class PaymentMethodFactory(factory.Factory):
    id = factory.LazyAttribute(lambda _: fake.uuid4())
    created_at = factory.LazyAttribute(lambda _: datetime.now())
    confirmable = False

    class Meta:
        model = domain.PaymentMethod
