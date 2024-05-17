import pytest
import responses

from acquiring.contrib import paypal


@responses.activate
def test_givenInvalidCredentials_whenInstantiatingTheAdapter_thenAnUnauthorizedResponseIsReturned() -> None:
    responses.add(
        responses.POST,
        f"https://api-m.sandbox.paypal.com/{paypal.adapter.GET_ACCESS_TOKEN}",
        body='{"error":"invalid_client","error_description":"Client Authentication failed"}',
        status=401,
        content_type="application/json",
    )

    with pytest.raises(paypal.adapter.UnauthorizedError):
        paypal.adapter.PayPalAdapter(
            base_url="https://api-m.sandbox.paypal.com/",
            client_id="TEST_CLIENT_ID",
            client_secret="TEST_CLIENT_SECRET",
            callback_url="https://www.example.com",
            webhook_id="LONG_ID",
        )


@responses.activate
def test_givenValidCredentials_whenInstantiatingTheAdapter_thenAccessTokenIsRetrievedFromPayPal() -> None:
    token = "long-token"
    responses.add(
        responses.POST,
        f"https://api-m.sandbox.paypal.com/{paypal.adapter.GET_ACCESS_TOKEN}",
        json={
            "scope": "https://uri.paypal.com/services/invoicing https://uri.paypal.com/services/disputes/read-buyer https://uri.paypal.com/services/payments/realtimepayment https://uri.paypal.com/services/disputes/update-seller https://uri.paypal.com/services/payments/payment/authcapture openid https://uri.paypal.com/services/disputes/read-seller https://uri.paypal.com/services/payments/refund https://api-m.paypal.com/v1/vault/credit-card https://api-m.paypal.com/v1/payments/.* https://uri.paypal.com/payments/payouts https://api-m.paypal.com/v1/vault/credit-card/.* https://uri.paypal.com/services/subscriptions https://uri.paypal.com/services/applications/webhooks",
            "access_token": token,
            "token_type": "Bearer",
            "app_id": "APP-80W284485P519543T",
            "expires_in": 31668,
            "nonce": "2020-04-03T15:35:36ZaYZlGvEkV4yVSz8g6bAKFoGSEzuy3CQcz3ljhibkOHg",
        },
        status=201,
        content_type="application/json",
    )

    adapter = paypal.adapter.PayPalAdapter(
        base_url="https://api-m.sandbox.paypal.com/",
        client_id="TEST_CLIENT_ID",
        client_secret="TEST_CLIENT_SECRET",
        callback_url="https://www.example.com",
        webhook_id="LONG_ID",
    )
    assert adapter.access_token == token


def test_givenABaseUrlThatDoesNotEndInSlash_whenInstantiatingTheAdapter_thenABadUrlErrorIsRaised() -> None:
    with pytest.raises(paypal.adapter.BadUrlError):
        paypal.adapter.PayPalAdapter(
            base_url="https://bad-url.com",
            client_id="TEST_CLIENT_ID",
            client_secret="TEST_CLIENT_SECRET",
            callback_url="https://www.example.com",
            webhook_id="LONG_ID",
        )
