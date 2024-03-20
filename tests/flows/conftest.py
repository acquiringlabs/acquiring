import uuid
from typing import Dict, List

import pytest

from django_acquiring import domain
from django_acquiring.protocols.enums import OperationStatusEnum
from django_acquiring.protocols.flows import AbstractBlock, AbstractBlockResponse
from django_acquiring.protocols.payments import AbstractPaymentMethod, AbstractPaymentOperation
from django_acquiring.protocols.repositories import AbstractRepository


@pytest.fixture
def fake_payment_method_repository():
    from tests.factories import PaymentMethodFactory

    class FakePaymentMethodRepository:

        def __init__(self, db_payment_methods: list | None = None):
            self.db_payment_methods = db_payment_methods or []

        def add(self, data: dict) -> AbstractPaymentMethod:
            db_payment_method = PaymentMethodFactory(
                payment_method_id=data.get("payment_method_id", uuid.uuid4()),
                confirmable=data.get("confirmable"),
            )
            self.db_payment_methods.append(db_payment_method)
            return db_payment_method.to_domain()

        def get(self, id: uuid.UUID) -> AbstractPaymentMethod:
            for pm in self.db_payment_methods:
                if pm.id == id:
                    return pm.to_domain()
            raise domain.PaymentMethod.DoesNotExist

    assert issubclass(FakePaymentMethodRepository, AbstractRepository)
    return FakePaymentMethodRepository


@pytest.fixture
def fake_payment_operation_repository():
    from tests.factories import PaymentOperationFactory

    class FakePaymentOperationRepository:

        def __init__(self, db_payment_operations: list | None = None):
            self.db_payment_operations = db_payment_operations or []

        def add(self, payment_method, type, status) -> AbstractPaymentOperation:
            payment_operation = PaymentOperationFactory(payment_method_id=payment_method.id, type=type, status=status)
            payment_method.payment_operations.append(payment_operation)
            return payment_operation

        def get(self, id: uuid.UUID): ...

    assert issubclass(FakePaymentOperationRepository, AbstractRepository)
    return FakePaymentOperationRepository


@pytest.fixture(scope="module")
def fake_block():
    class FakeBlock:

        def __init__(
            self,
            fake_response_status: OperationStatusEnum = OperationStatusEnum.completed,
            fake_response_actions: List[Dict] | None = None,
        ):
            self.response_status = fake_response_status
            self.response_actions = fake_response_actions or []

        def run(self, payment_method: AbstractPaymentMethod) -> AbstractBlockResponse:
            return domain.BlockResponse(
                status=self.response_status,
                actions=self.response_actions,
                payment_method=payment_method,
            )

    assert issubclass(FakeBlock, AbstractBlock)
    return FakeBlock


@pytest.fixture(scope="module")
def fake_process_actions_block():

    class FakeProcessActionsBlock:

        def __init__(
            self,
            fake_response_status: OperationStatusEnum = OperationStatusEnum.completed,
        ):
            self.response_status = fake_response_status

        def run(self, payment_method: AbstractPaymentMethod, action_data: Dict) -> AbstractBlockResponse:
            return domain.BlockResponse(status=self.response_status, payment_method=payment_method)

    assert issubclass(FakeProcessActionsBlock, AbstractBlock)
    return FakeProcessActionsBlock
