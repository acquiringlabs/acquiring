import random

import factory
from faker import Faker

from acquiring.utils import is_django_installed

fake = Faker()


if is_django_installed():

    class PaymentAttemptFactory(factory.django.DjangoModelFactory):
        currency = factory.LazyAttribute(lambda _: fake.currency_code())
        amount = factory.LazyAttribute(lambda _: random.randint(0, 999999))

        class Meta:
            model = "acquiring.PaymentAttempt"

    class PaymentMethodFactory(factory.django.DjangoModelFactory):

        confirmable = False

        class Meta:
            model = "acquiring.PaymentMethod"

    class PaymentOperationFactory(factory.django.DjangoModelFactory):
        class Meta:
            model = "acquiring.PaymentOperation"

    class TokenFactory(factory.django.DjangoModelFactory):
        class Meta:
            model = "acquiring.Token"

    class ItemFactory(factory.django.DjangoModelFactory):
        class Meta:
            model = "acquiring.Item"

        name = factory.LazyAttribute(lambda _: fake.name())
        quantity = factory.LazyAttribute(lambda _: random.randint(0, 999999))
        unit_price = factory.LazyAttribute(lambda _: random.randint(0, 999999))

    class BlockEventFactory(factory.django.DjangoModelFactory):
        class Meta:
            model = "acquiring.BlockEvent"
