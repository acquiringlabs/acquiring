from faker import Faker
from acquiring import storage, utils
from tests.storage.utils import skip_if_sqlalchemy_not_installed

fake = Faker()

if utils.is_sqlalchemy_installed():
    from sqlalchemy import orm
    from tests.storage.sqlalchemy import factories


@skip_if_sqlalchemy_not_installed
def test_givenExistingPaymentMethodRow_whenCallingRepositoryGet_thenPaymentGetsRetrieved(
    session: "orm.Session",
) -> None:
    payment_attempt = factories.PaymentAttemptFactory()
    payment_method = factories.PaymentMethodFactory(payment_attempt=payment_attempt)

    result = storage.sqlalchemy.PaymentMethodRepository(
        session=session,
    ).get(id=payment_method.id)

    assert result.payment_attempt == payment_attempt.to_domain()
    assert result == payment_method.to_domain()
