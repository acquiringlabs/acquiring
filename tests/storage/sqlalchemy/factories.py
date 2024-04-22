import factory
from faker import Faker

from acquiring import utils

fake = Faker()


if utils.is_sqlalchemy_installed():
    from acquiring.storage.sqlalchemy import models

    class PaymentAttemptFactory(factory.alchemy.SQLAlchemyModelFactory):
        # currency = factory.LazyAttribute(lambda _: fake.currency_code())
        # amount = factory.LazyAttribute(lambda _: random.randint(0, 999999))

        class Meta:
            model = models.PaymentAttempt
            sqlalchemy_session = models.session
            sqlalchemy_session_persistence = "commit"

    class PaymentMethodFactory(factory.alchemy.SQLAlchemyModelFactory):
        confirmable = factory.LazyAttribute(lambda _: fake.boolean())

        class Meta:
            model = models.PaymentMethod
            sqlalchemy_session = models.session
            sqlalchemy_session_persistence = "commit"
