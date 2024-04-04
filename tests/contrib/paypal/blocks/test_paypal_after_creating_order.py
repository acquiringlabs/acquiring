from datetime import datetime

import pytest
from django.utils import timezone
from faker import Faker

from django_acquiring import domain, enums, models, repositories
from django_acquiring.contrib import paypal
from tests.django.factories import PaymentAttemptFactory, PaymentMethodFactory

fake = Faker()


@pytest.mark.django_db
def test_givenACorrectPaymentMethod_whenRunningPayPalAfterCreatingOrder_thenItCompletesPayment() -> None:

    payment_method = PaymentMethodFactory(payment_attempt=PaymentAttemptFactory()).to_domain()

    block = paypal.blocks.PayPalAfterCreatingOrder(
        transaction_repository=repositories.TransactionRepository(),
    )

    external_id = "WH-684457241H310260F-0FC94184GF055315P"
    fake_create_time = timezone.now().isoformat()
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
            "create_time": timezone.now().isoformat(),
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

    transactions = models.Transaction.objects.all()

    assert len(transactions) == 1
    transaction = transactions[0]

    assert transaction.to_domain() == domain.Transaction(
        external_id=external_id,
        timestamp=datetime.fromisoformat(fake_create_time),
        raw_data=raw_data,
        provider_name="paypal",
        payment_method_id=payment_method.id,
    )
