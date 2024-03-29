import random

import factory
from faker import Faker

fake = Faker()


class PaymentAttemptFactory(factory.django.DjangoModelFactory):
    currency = factory.LazyAttribute(lambda _: fake.currency_code())
    amount = factory.LazyAttribute(lambda _: random.randint(0, 999999))

    class Meta:
        model = "django_acquiring.PaymentAttempt"


class PaymentMethodFactory(factory.django.DjangoModelFactory):

    confirmable = False

    class Meta:
        model = "django_acquiring.PaymentMethod"


class PaymentOperationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "django_acquiring.PaymentOperation"


class TokenFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "django_acquiring.Token"


class ItemFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "django_acquiring.Item"

    name = factory.LazyAttribute(lambda _: fake.name())
    quantity = factory.LazyAttribute(lambda _: random.randint(0, 999999))
    unit_price = factory.LazyAttribute(lambda _: random.randint(0, 999999))
