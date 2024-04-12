import factory
from faker import Faker

from acquiring import models, utils

fake = Faker()


if utils.is_sqlalchemy_installed():

    class PaymentAttemptFactory(factory.alchemy.SQLAlchemyModelFactory):
        # currency = factory.LazyAttribute(lambda _: fake.currency_code())
        # amount = factory.LazyAttribute(lambda _: random.randint(0, 999999))

        class Meta:
            model = models.PaymentAttempt
            sqlalchemy_session = models.sessionmaker()
            sqlalchemy_session_persistence = "commit"
