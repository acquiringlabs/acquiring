import base64
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional
from urllib.parse import urljoin
from uuid import UUID

import requests

from acquiring import domain, protocols

from .domain import Order, OrderIntentEnum, PayPalStatusEnum


@dataclass(match_args=False)
class PayPalResponse:
    external_id: Optional[str]
    timestamp: Optional[datetime]
    raw_data: dict
    status: PayPalStatusEnum
    intent: OrderIntentEnum


GET_ACCESS_TOKEN = "v1/oauth2/token"
CREATE_WEBHOOK = "v1/notifications/webhooks"
CREATE_ORDER = "/v2/checkout/orders"


@dataclass
class PayPalAdapter:
    """
    PayPal APIs use REST, authenticate with OAuth 2.0 access tokens,
    and return HTTP response codes and responses encoded in JSON.
    """

    base_url: str
    callback_url: str
    client_id: str
    client_secret: str
    provider_name: str = "paypal"
    webhook_id: Optional[str] = None

    access_token: str = field(init=False)
    scope: list[str] = field(init=False)
    expires_in: int = field(init=False)

    def __repr__(self) -> str:
        """String representation of the class"""
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

        self._authenticate()
        if self.webhook_id is None:
            self._subscribe_to_webhook_events()

    @domain.wrapped_by_transaction
    def create_order(
        self,
        unit_of_work: "protocols.UnitOfWork",
        payment_method: "protocols.PaymentMethod",
        request_id: UUID,
        order: Order,
    ) -> "protocols.AdapterResponse":
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
            "payment_source": {
                "paypal": {
                    "experience_context": {
                        "payment_method_preference": "IMMEDIATE_PAYMENT_REQUIRED",
                        "locale": "en-US",
                        "shipping_preference": "NO_SHIPPING",
                        "user_action": "PAY_NOW",
                        "return_url": "https://example.com/returnUrl",
                        "cancel_url": "https://example.com/cancelUrl",
                    },
                },
            },
        }

        try:
            response = requests.post(url, json=data, headers=headers)
            response.raise_for_status()
        except requests.exceptions.HTTPError:
            return PayPalResponse(
                external_id=None,
                timestamp=None,
                raw_data=response.json(),
                status=PayPalStatusEnum.FAILED,
                intent=order.intent,
            )

        serialized_response = response.json()
        return PayPalResponse(
            external_id=serialized_response["id"],
            timestamp=(
                datetime.fromisoformat(serialized_response["create_time"])
                if serialized_response.get("create_time")
                else datetime.now(timezone.utc)
            ),
            raw_data=serialized_response,
            status=PayPalStatusEnum(serialized_response["status"]),
            intent=OrderIntentEnum(serialized_response["intent"]),
        )

    def _authenticate(self) -> None:
        url = urljoin(self.base_url, GET_ACCESS_TOKEN)

        credentials_b64 = base64.b64encode(f"{self.client_id}:{self.client_secret}".encode()).decode()

        headers = {
            "Authorization": f"Basic {credentials_b64}",
            "Content-Type": "application/x-www-form-urlencoded",
        }

        try:
            response = requests.post(url, headers=headers, data={"grant_type": "client_credentials"})
            response.raise_for_status()

            serialized_response = response.json()
            self.scope = serialized_response["scope"].split(" ")
            self.access_token = serialized_response["access_token"]
            self.expires_in = serialized_response["expires_in"]

        except requests.exceptions.HTTPError as exception:
            raise UnauthorizedError(*exception.args)

    def _subscribe_to_webhook_events(self) -> None:
        assert self.access_token is not None

        url = urljoin(self.base_url, CREATE_WEBHOOK)

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.access_token}",
        }

        try:
            response = requests.post(
                url,
                headers=headers,
                data=json.dumps(
                    {
                        "url": f"{self.callback_url}",
                        "event_types": [
                            {"name": "*"},
                        ],
                    }
                ),
            )
            response.raise_for_status()
        except requests.exceptions.HTTPError:
            raise UnauthorizedError(response.text)

        self.webhook_id = response.json()["id"]


class UnauthorizedError(Exception):
    pass


class BadRequestError(Exception):
    pass


class BadUrlError(Exception):
    pass
