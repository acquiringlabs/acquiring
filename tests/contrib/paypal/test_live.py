import operator
import os
import uuid

import pytest
from dotenv import load_dotenv

from django_acquiring.contrib import paypal
from tests.repositories import factories

load_dotenv()  # take environment variables from .env.

# TODO Find a way to make sure never to commit this test unskipped


@pytest.mark.skip(reason="Use only to check that the credentials in .env are valid")
class TestLiveSandbox:
    """
    These tests are meant to check against the sandbox environment.

    Therefore, they aren't meant to be run normally, unless you want to check that the code
    works against the sandbox environment. Otherwise, they must be skipped.
    """

    BASE_URL = "https://api-m.sandbox.paypal.com/"

    @pytest.mark.django_db
    def test_givenCorrectCredentials_weCanCreateAnOrder(self) -> None:
        adapter = paypal.PayPalAdapter(
            self.BASE_URL,
            client_id=os.environ["PAYPAL_CLIENT_ID"],
            client_secret=os.environ["PAYPAL_CLIENT_SECRET"],
            callback_url=os.environ["CALLBACK_URL"],  # Check https://webhook-test.com/
            webhook_id=os.environ.get("WEBHOOK_ID"),
        )
        assert adapter.access_token is not None
        assert adapter.webhook_id is not None
        print("***")
        print(adapter.webhook_id)
        print("***")

        payment_method = factories.PaymentMethodFactory(payment_attempt=factories.PaymentAttemptFactory()).to_domain()

        response = adapter.create_order(
            payment_method=payment_method,
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
                    paypal.PurchaseUnit(
                        reference_id=str(uuid.uuid4()),
                        amount=paypal.Amount(
                            currency_code="USD",
                            value="20.00",
                        ),
                    ),
                ],
            ),
        )

        assert response.external_id is not None, response.raw_data
        assert response.status == paypal.PayPalStatusEnum.PAYER_ACTION_REQUIRED
        assert response.timestamp is not None

        raw_data = response.raw_data

        assert len(raw_data.get("purchase_units", [])) == 2, raw_data

        assert raw_data.get("links") is not None, raw_data
        assert len(raw_data["links"]) == 2
        assert set(link["rel"] for link in raw_data["links"]) == set(["payer-action", "self"])
        links = sorted(raw_data["links"], key=operator.itemgetter("rel"))  # ordered by rel
        redirect_link = links[0]
        assert redirect_link["href"] == f"https://www.sandbox.paypal.com/checkoutnow?token={response.external_id}"

        print("***")
        print(redirect_link["href"])
        print("***")
