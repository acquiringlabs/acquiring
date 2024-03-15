import uuid
from typing import Dict, List

import pytest

from django_acquiring.flows.domain.blocks import BlockResponse
from django_acquiring.payments.domain import PaymentMethod
from django_acquiring.protocols.flows import AbstractBlock, AbstractBlockResponse
from django_acquiring.protocols.payments import (
    AbstractPaymentMethod,
    AbstractPaymentOperation,
    PaymentOperationStatusEnum,
)
from django_acquiring.protocols.repositories import AbstractRepository


@pytest.fixture
def fake_payment_method_repository():
    from tests.factories import PaymentMethodFactory

    class FakePaymentMethodRepository:

        def __init__(self, db_payment_methods: list | None = None):
            self.db_payment_methods = db_payment_methods or []

        def add(self, data: dict) -> AbstractPaymentMethod:
            db_payment_method = PaymentMethodFactory(payment_method_id=data.get("payment_method_id", uuid.uuid4()))
            self.db_payment_methods.append(db_payment_method)
            return db_payment_method.to_domain()

        def get(self, id: uuid.UUID) -> AbstractPaymentMethod:
            for pm in self.db_payment_methods:
                if pm.id == id:
                    return pm.to_domain()
            raise PaymentMethod.DoesNotExist

    assert issubclass(FakePaymentMethodRepository, AbstractRepository)
    return FakePaymentMethodRepository


@pytest.fixture
def fake_initialize_block():

    class FakeInitializeBlock:

        def __init__(
            self,
            fake_response_status: PaymentOperationStatusEnum = PaymentOperationStatusEnum.completed,
            fake_response_actions: List[Dict] | None = None,
        ):
            self.response_status = fake_response_status
            self.response_actions = fake_response_actions or []

        def run(self, payment_method: AbstractPaymentMethod) -> AbstractBlockResponse:
            return BlockResponse(
                status=self.response_status,
                actions=self.response_actions,
                payment_method=payment_method,
            )

    assert issubclass(FakeInitializeBlock, AbstractBlock)
    return FakeInitializeBlock


@pytest.fixture
def fake_pay_block():

    class FakePayBlock:

        def __init__(self, fake_response_status: PaymentOperationStatusEnum):
            self.response_status = fake_response_status

        def run(self, payment_method: AbstractPaymentMethod) -> AbstractBlockResponse:
            return BlockResponse(status=self.response_status, payment_method=payment_method)

    return FakePayBlock


@pytest.fixture
def fake_process_actions_block():

    class FakeProcessActionsBlock:

        def __init__(
            self,
            fake_response_status: PaymentOperationStatusEnum = PaymentOperationStatusEnum.completed,
        ):
            self.response_status = fake_response_status

        def run(self, payment_method: AbstractPaymentMethod, action_data: Dict) -> AbstractBlockResponse:
            return BlockResponse(status=self.response_status, payment_method=payment_method)

    assert issubclass(FakeProcessActionsBlock, AbstractBlock)
    return FakeProcessActionsBlock


@pytest.fixture
def fake_payment_operation_repository():
    from tests.factories import PaymentOperationFactory

    class FakePaymentOperationRepository:

        def __init__(self, db_payment_operations: list | None = None):
            self.db_payment_operations = db_payment_operations or []

        def add(self, payment_method, type, status) -> AbstractPaymentOperation:
            return PaymentOperationFactory(payment_method_id=payment_method.id, type=type, status=status)

        def get(self, id: uuid.UUID): ...

    assert issubclass(FakePaymentOperationRepository, AbstractRepository)
    return FakePaymentOperationRepository
