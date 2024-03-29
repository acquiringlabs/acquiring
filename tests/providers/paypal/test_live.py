import operator
import os
import pprint
import uuid

import pytest
from dotenv import load_dotenv

from django_acquiring.providers import paypal
from tests.factories import PaymentAttemptFactory, PaymentMethodFactory

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
        )
        assert adapter.access_token is not None

        payment_method = PaymentMethodFactory(payment_attempt=PaymentAttemptFactory()).to_domain()

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
                ],
            ),
        )

        assert response.external_id is not None
        assert response.status == paypal.PayPalStatusEnum.CREATED
        assert response.intent == paypal.OrderIntentEnum.CAPTURE
        assert response.timestamp is not None

        raw_data = response.raw_data
        assert raw_data.get("links") is not None
        assert len(raw_data["links"]) == 4
        assert set(link["rel"] for link in raw_data["links"]) == set(["approve", "capture", "self", "update"])
        links = sorted(raw_data["links"], key=operator.itemgetter("rel"))  # ordered by rel
        approve_link = links[0]
        assert approve_link["href"] == f"https://www.sandbox.paypal.com/checkoutnow?token={response.external_id}"

        print("***")
        pprint.pprint(response.raw_data)
        print("***")
