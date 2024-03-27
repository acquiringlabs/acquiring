import os
import uuid

from dotenv import load_dotenv

from django_acquiring.providers import paypal

load_dotenv()  # take environment variables from .env.


# @pytest.mark.skip(reason="Use only to check that the credentials in .env are valid")
class TestLiveSandbox:
    """
    These tests are meant to check against the sandbox environment.

    Therefore, they aren't meant to be run normally, unless you want to check that the code
    works against the sandbox environment. Otherwise, they must be skipped.
    """

    BASE_URL = "https://api-m.sandbox.paypal.com/"

    def test_givenCorrectCredentials_weCanCreateAnOrder(self) -> None:
        adapter = paypal.PayPalAdapter(
            self.BASE_URL,
            client_id=os.environ["PAYPAL_CLIENT_ID"],
            client_secret=os.environ["PAYPAL_CLIENT_SECRET"],
        )
        assert adapter.access_token is not None

        response = adapter.create_order(
            request_id=uuid.uuid4(),
            order=paypal.Order(
                intent=paypal.OrderIntentEnum.CAPTURE,
                purchase_units=[
                    paypal.PurchaseUnit(
                        reference_id=str(uuid.uuid4()),
                        amount=paypal.Amount(
                            currency_code="USD",
                            value="10.00",
                        ),
                    ),
                ],
            ),
        )

        print(response.unparsed_data)
        assert response.status == paypal.PayPalStatusEnum.CREATED
        assert response.transaction_id is not None
