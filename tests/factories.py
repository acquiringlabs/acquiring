import random

import factory
from faker import Faker

fake = Faker()


class OrderFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "django_acquiring.Order"


class PaymentAttemptFactory(factory.django.DjangoModelFactory):
    order = factory.SubFactory(OrderFactory)
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
