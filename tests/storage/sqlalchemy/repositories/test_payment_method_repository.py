from faker import Faker

from acquiring import utils
from tests.storage.utils import skip_if_sqlalchemy_not_installed

fake = Faker()

if utils.is_sqlalchemy_installed():
    from tests.storage.sqlalchemy import factories


@skip_if_sqlalchemy_not_installed
def test_sqlalchemyFactoriesWorkProperly() -> None:
    payment_attempt = factories.PaymentAttemptFactory()
    factories.PaymentMethodFactory(payment_attempt=payment_attempt)
