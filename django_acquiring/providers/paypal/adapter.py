import base64
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from urllib.parse import urljoin
from uuid import UUID

import requests

from .domain import Order, OrderIntentEnum, PayPalStatusEnum


# TODO Create AbstractAdapterResponse, wrapped_by_transactions
@dataclass
class PayPalResponse:
    status: PayPalStatusEnum
    intent: OrderIntentEnum
    create_time: Optional[datetime]
    transaction_id: Optional[str]
    unparsed_data: dict


GET_ACCESS_TOKEN = "v1/oauth2/token"
CREATE_ORDER = "/v2/checkout/orders"


@dataclass
class PayPalAdapter:
    """
    PayPal APIs use REST, authenticate with OAuth 2.0 access tokens,
    and return HTTP response codes and responses encoded in JSON.

    When accessing the adapter, an access token is requested to PayPal
    >>> import responses
    >>> with responses.RequestsMock() as rsps:
    ...     rsps.add(
    ...         responses.POST,
    ...         f"https://api-m.sandbox.paypal.com/{GET_ACCESS_TOKEN}",
    ...         body='{"error":"invalid_client","error_description":"Client Authentication failed"}',
    ...         status=401,
    ...         content_type="application/json",
    ...     )
    ...     PayPalAdapter(
    ...         base_url="https://api-m.sandbox.paypal.com/",
    ...         client_id="TEST_CLIENT_ID",
    ...         client_secret="TEST_CLIENT_SECRET"
    ...     )
    Traceback (most recent call last):
        ...
    django_acquiring.providers.paypal.adapter.UnauthorizedError: 401 Client Error: Unauthorized for url: https://api-m.sandbox.paypal.com/v1/oauth2/token

    When accessing the adapter with valid credentials, an access token is retrieved from PayPal
    >>> import responses
    >>> with responses.RequestsMock() as rsps:
    ...     rsps.add(
    ...         responses.POST,
    ...         f"https://api-m.sandbox.paypal.com/{GET_ACCESS_TOKEN}",
    ...         json={
    ...             "scope": "https://uri.paypal.com/services/invoicing https://uri.paypal.com/services/disputes/read-buyer https://uri.paypal.com/services/payments/realtimepayment https://uri.paypal.com/services/disputes/update-seller https://uri.paypal.com/services/payments/payment/authcapture openid https://uri.paypal.com/services/disputes/read-seller https://uri.paypal.com/services/payments/refund https://api-m.paypal.com/v1/vault/credit-card https://api-m.paypal.com/v1/payments/.* https://uri.paypal.com/payments/payouts https://api-m.paypal.com/v1/vault/credit-card/.* https://uri.paypal.com/services/subscriptions https://uri.paypal.com/services/applications/webhooks",
    ...             "access_token": "long-token",
    ...             "token_type": "Bearer",
    ...             "app_id": "APP-80W284485P519543T",
    ...             "expires_in": 31668,
    ...             "nonce": "2020-04-03T15:35:36ZaYZlGvEkV4yVSz8g6bAKFoGSEzuy3CQcz3ljhibkOHg"
    ...         },
    ...         status=201,
    ...         content_type="application/json",
    ...     )
    ...     PayPalAdapter(
    ...         base_url="https://api-m.sandbox.paypal.com/",
    ...         client_id="TEST_CLIENT_ID",
    ...         client_secret="TEST_CLIENT_SECRET"
    ...     )
    <Response(url='https://api-m.sandbox.paypal.com/v1/oauth2/token' status=201 content_type='application/json' headers='null')>
    PayPalAdapter:base_url=https://api-m.sandbox.paypal.com/|access_token=long-token|expires in 31668 seconds

    A base url that doesn't end in / is invalid
    >>> PayPalAdapter(
    ...     base_url="https://bad-url.com",
    ...     client_id="TEST_CLIENT_ID",
    ...     client_secret="TEST_CLIENT_SECRET"
    ... )
    Traceback (most recent call last):
        ...
    django_acquiring.providers.paypal.adapter.BadUrlError: base_url must end with /
    """

    base_url: str
    client_id: str
    client_secret: str

    access_token: str = field(init=False, repr=False)
    scope: list[str] = field(init=False, repr=False)
    expires_in: int = field(init=False, repr=False)

    def __repr__(self) -> str:
        return f"PayPalAdapter:base_url={self.base_url}|access_token={self.access_token}|expires in {self.expires_in} seconds"

    def __post_init__(self) -> None:
        """
        PayPal integrations use a client ID and client secret to authenticate API calls.

        Exchange your client ID and client secret for access token, scope,
        and the number of seconds the access token is valid.

        See
        https://developer.paypal.com/api/rest/#link-sampleresponse
        """
        # https://stackoverflow.com/questions/10893374/python-confusions-with-urljoin#10893427
        if not self.base_url.endswith("/"):
            raise BadUrlError("base_url must end with /")

        url = urljoin(self.base_url, GET_ACCESS_TOKEN)

        # Encode client ID and secret in Base64
        credentials = f"{self.client_id}:{self.client_secret}"
        credentials_b64 = base64.b64encode(credentials.encode()).decode()

        headers = {"Authorization": f"Basic {credentials_b64}", "Content-Type": "application/x-www-form-urlencoded"}

        try:
            response = requests.post(url, headers=headers, data={"grant_type": "client_credentials"})
            response.raise_for_status()
        except requests.exceptions.HTTPError as exception:
            raise UnauthorizedError(*exception.args)

        serialized_response = response.json()
        self.scope = serialized_response["scope"].split(" ")
        self.access_token = serialized_response["access_token"]
        self.expires_in = serialized_response["expires_in"]

    def create_order(self, request_id: UUID, order: Order) -> PayPalResponse:
        url = urljoin(self.base_url, CREATE_ORDER)

        headers = {
            "Content-Type": "application/json",
            "PayPal-Request-Id": str(request_id),
            "Authorization": f"Bearer {self.access_token}",
            "Prefer": "return=representation",
        }
        data = {
            "intent": order.intent,
            "purchase_units": [
                {
                    "reference_id": str(purchase_unit.reference_id),
                    "amount": {
                        "currency_code": purchase_unit.amount.currency_code,
                        "value": purchase_unit.amount.value,
                    },
                }
                for purchase_unit in order.purchase_units
            ],
        }
        try:
            response = requests.post(url, json=data, headers=headers)
            response.raise_for_status()
        except requests.exceptions.HTTPError:
            return PayPalResponse(
                status=PayPalStatusEnum.FAILED,
                intent=order.intent,
                create_time=None,
                transaction_id=None,
                unparsed_data=response.json(),
            )

        serialized_response = response.json()
        return PayPalResponse(
            status=PayPalStatusEnum(serialized_response["status"]),
            intent=OrderIntentEnum(serialized_response["intent"]),
            create_time=datetime.fromisoformat(serialized_response["create_time"]),
            transaction_id=serialized_response["id"],
            unparsed_data=serialized_response,
        )


class UnauthorizedError(Exception):
    pass


class BadRequestError(Exception):
    pass


class BadUrlError(Exception):
    pass
