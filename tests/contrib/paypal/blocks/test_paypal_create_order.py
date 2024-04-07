import os
import uuid
from datetime import datetime, timezone
from typing import Callable, Generator

import responses
from faker import Faker

from acquiring import domain, enums, protocols
from acquiring.contrib import paypal

fake = Faker()


@responses.activate
def test_givenACorrectPaymentMethod_whenRunningPayPalCreateOrder_thenItReturnsRedirectAction(  # type:ignore[misc]
    fake_os_environ: Generator,
    fake_transaction_repository: Callable[
        ...,
        protocols.AbstractRepository,
    ],
    fake_block_event_repository: Callable[
        ...,
        protocols.AbstractRepository,
    ],
) -> None:
    payment_method = domain.PaymentMethod(
        id=uuid.uuid4(),
        created_at=datetime.now(),
        payment_attempt=domain.PaymentAttempt(
            id=uuid.uuid4(),
            created_at=datetime.now(),
            amount=30,
            currency="USD",
        ),
        confirmable=False,
    )

    responses.add(
        responses.POST,
        f"{os.environ['PAYPAL_BASE_URL']}v1/oauth2/token",
        json={
            "scope": "",
            "access_token": fake.password(length=40, special_chars=False, upper_case=False),
            "token_type": "Bearer",
            "app_id": "APP-S3CR3T",
            "expires_in": 31668,
            "nonce": f"{datetime.now(timezone.utc).isoformat()}-{fake.password(length=40, special_chars=False, upper_case=False)}",
        },
        status=201,
        content_type="application/json",
    )

    repository = fake_block_event_repository()

    block = paypal.blocks.PayPalCreateOrder(
        block_event_repository=repository,
        adapter=paypal.adapter.PayPalAdapter(
            base_url=os.environ["PAYPAL_BASE_URL"],
            client_id=os.environ["PAYPAL_CLIENT_ID"],
            client_secret=os.environ["PAYPAL_CLIENT_SECRET"],
            transaction_repository=fake_transaction_repository(),
            callback_url=fake.url(),
            webhook_id=fake.isbn10(),
        ),
    )

    fake_create_time = datetime.now(timezone.utc).isoformat()
    fake_id = fake.password(length=10, special_chars=False, upper_case=False).upper()
    approve_url = f"{fake.url()}?token={fake_id}"

    raw_response = {
        "create_time": fake_create_time,
        "id": fake_id,
        "intent": paypal.domain.OrderIntentEnum.CAPTURE,
        "links": [
            {"href": fake.url(), "method": "GET", "rel": "self"},
            {"href": approve_url, "method": "GET", "rel": "approve"},
            {"href": fake.url(), "method": "PATCH", "rel": "update"},
            {"href": fake.url(), "method": "POST", "rel": "capture"},
        ],
        "purchase_units": [
            {
                "amount": {"currency_code": "USD", "value": "10.00"},
                "payee": {
                    "email_address": fake.email(),
                    "merchant_id": fake.password(length=10, special_chars=False, upper_case=False).upper(),
                },
                "reference_id": fake.uuid4(),
            }
        ],
        "status": paypal.domain.PayPalStatusEnum.CREATED,
    }

    responses.add(
        responses.Response(
            responses.POST,
            f"{os.environ['PAYPAL_BASE_URL']}v2/checkout/orders",
            json=raw_response,
        )
    )

    response = block.run(payment_method)

    assert response == domain.BlockResponse(
        status=enums.OperationStatusEnum.COMPLETED,
        actions=[{"redirect_url": approve_url}],
        error_message=None,
    )

    block_events: list[domain.BlockEvent] = repository.units  # type:ignore[attr-defined]
    assert len(block_events) == 2
    assert [block.status for block in block_events] == [
        enums.OperationStatusEnum.STARTED,
        enums.OperationStatusEnum.COMPLETED,
    ]

    # assert models.Transaction.objects.count() == 1
    # transaction = models.Transaction.objects.first()
    # assert transaction.to_domain() == domain.Transaction(
    #     external_id=fake_id,
    #     timestamp=datetime.fromisoformat(fake_create_time),
    #     provider_name="paypal",
    #     payment_method_id=payment_method.id,
    #     raw_data=raw_response,
    # )
