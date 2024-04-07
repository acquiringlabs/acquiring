import uuid
from datetime import datetime, timezone
from typing import Callable

from faker import Faker

from acquiring import domain, enums, protocols
from acquiring.contrib import paypal

fake = Faker()


# TODO implement hypothesis
def test_givenACorrectPaymentMethod_whenRunningPayPalAfterCreatingOrder_thenItCompletesPayment(  # type:ignore[misc]
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

    block_event_repository = fake_block_event_repository()
    transaction_repository = fake_transaction_repository()

    block = paypal.blocks.PayPalAfterCreatingOrder(
        block_event_repository=block_event_repository,
        transaction_repository=transaction_repository,
    )

    external_id = "WH-684457241H310260F-0FC94184GF055315P"
    fake_create_time = datetime.now(timezone.utc).isoformat()
    fake_merchant_id = fake.md5()
    fake_currency = fake.currency_code()
    payee_email = fake.email()
    payer_email = fake.email()
    payer_first_name = fake.first_name()
    payer_last_name = fake.last_name()
    payer_country = fake.country_code()
    payer_id = fake.md5()

    raw_data = {
        "id": external_id,
        "event_version": "1.0",
        "create_time": fake_create_time,
        "resource_type": "checkout-order",
        "resource_version": "2.0",
        "event_type": "CHECKOUT.ORDER.APPROVED",
        "summary": fake.sentence(),
        "resource": {
            "create_time": datetime.now(timezone.utc).isoformat(),
            "purchase_units": [
                {
                    "reference_id": fake.uuid4(),
                    "amount": {"currency_code": fake_currency, "value": "10.00"},
                    "payee": {
                        "email_address": payee_email,
                        "merchant_id": fake_merchant_id,
                    },
                },
                {
                    "reference_id": fake.uuid4(),
                    "amount": {"currency_code": fake_currency, "value": "20.00"},
                    "payee": {
                        "email_address": payee_email,
                        "merchant_id": fake_merchant_id,
                    },
                },
            ],
            "links": [
                {
                    "href": fake.url(),
                    "rel": fake.word(),
                    "method": fake.http_method(),
                }
                for _ in range(3)
            ],
            "id": "55855893X5198173A",
            "payment_source": {
                "paypal": {
                    "email_address": payer_email,
                    "account_id": payer_id,
                    "account_status": "VERIFIED",
                    "name": {
                        "given_name": payer_first_name,
                        "surname": payer_last_name,
                    },
                    "address": {"country_code": payer_country},
                }
            },
            "intent": "CAPTURE",
            "payer": {
                "name": {"given_name": payer_first_name, "surname": payer_last_name},
                "email_address": payer_email,
                "payer_id": payer_id,
                "address": {"country_code": payer_country},
            },
            "status": "APPROVED",
        },
        "links": [
            {
                "href": fake.url(),
                "rel": fake.word(),
                "method": fake.http_method(),
            }
            for _ in range(2)
        ],
    }

    response = block.run(
        payment_method,
        webhook_data=paypal.domain.PayPalWebhookData(
            id=raw_data["id"],
            event_version=raw_data["event_version"],
            create_time=datetime.fromisoformat(raw_data["create_time"]),
            resource_type=raw_data["resource_type"],
            resource_version=raw_data["resource_version"],
            event_type=raw_data["event_type"],
            summary=raw_data["summary"],
            raw_data=raw_data,
        ),
    )

    assert response == domain.BlockResponse(
        status=enums.OperationStatusEnum.COMPLETED,
        actions=[],
        error_message=None,
    )

    block_events: list[domain.BlockEvent] = block_event_repository.units  # type:ignore[attr-defined]
    assert len(block_events) == 2
    assert [block.status for block in block_events] == [
        enums.OperationStatusEnum.STARTED,
        enums.OperationStatusEnum.COMPLETED,
    ]

    transactions: list[domain.Transaction] = transaction_repository.units  # type:ignore[attr-defined]

    assert len(transactions) == 1

    assert transactions[0] == domain.Transaction(
        external_id=external_id,
        timestamp=datetime.fromisoformat(fake_create_time),
        raw_data=raw_data,
        provider_name="paypal",
        payment_method_id=payment_method.id,
    )
