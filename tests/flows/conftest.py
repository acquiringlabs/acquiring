import uuid

import pytest

from django_acquiring.protocols.payments import AbstractPaymentMethod, AbstractPaymentOperation
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

        def get(self, id: uuid.UUID) -> AbstractPaymentMethod | None:
            for pm in self.db_payment_methods:
                if pm.id == id:
                    return pm.to_domain()
            return None

    assert issubclass(FakePaymentMethodRepository, AbstractRepository)
    return FakePaymentMethodRepository


@pytest.fixture
def fake_payment_operation_repository():
    from tests.factories import PaymentOperationFactory

    class FakePaymentOperationRepository:

        def __init__(self, db_payment_operations: list | None = None):
            self.db_payment_operations = db_payment_operations or []

        def add(self, payment_method, type, status) -> AbstractPaymentOperation:
            return PaymentOperationFactory(payment_method_id=payment_method.id, type=type, status=status)

        def get(self, id: uuid.UUID) -> AbstractPaymentOperation | None:
            for po in self.db_payment_operations:
                if po.id == id:
                    return po.to_domain()
            return None

    assert issubclass(FakePaymentOperationRepository, AbstractRepository)
    return FakePaymentOperationRepository
