import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Callable, Optional, Sequence, Type

import pytest

from django_acquiring import domain, protocols
from django_acquiring.enums import OperationStatusEnum, OperationTypeEnum


@pytest.fixture(scope="module")
def fake_block() -> Type[protocols.AbstractBlock]:
    class FakeBlock:

        def __init__(
            self,
            *args: Sequence,
            **kwargs: dict,
        ):
            fake_response_status: OperationStatusEnum = kwargs.get(
                "fake_response_status", OperationStatusEnum.COMPLETED
            )  # type:ignore[assignment]

            fake_response_actions: list[dict] = kwargs.get("fake_response_actions", [])  # type:ignore[assignment]

            self.response_status = fake_response_status
            self.response_actions = fake_response_actions or []

        def run(
            self, payment_method: protocols.AbstractPaymentMethod, *args: Sequence, **kwargs: dict
        ) -> protocols.AbstractBlockResponse:
            return domain.BlockResponse(
                status=self.response_status,
                actions=self.response_actions,
            )

    assert issubclass(FakeBlock, protocols.AbstractBlock)
    return FakeBlock


@pytest.fixture(scope="module")
def fake_process_action_block() -> Type[protocols.AbstractBlock]:

    class FakeProcessActionsBlock:

        def __init__(
            self,
            fake_response_status: OperationStatusEnum = OperationStatusEnum.COMPLETED,
        ):
            self.response_status = fake_response_status

        def run(
            self, payment_method: protocols.AbstractPaymentMethod, *args: Sequence, **kwargs: dict
        ) -> protocols.AbstractBlockResponse:
            return domain.BlockResponse(status=self.response_status)

    assert issubclass(FakeProcessActionsBlock, protocols.AbstractBlock)
    return FakeProcessActionsBlock


@pytest.fixture(scope="module")
def fake_payment_method_repository() -> Callable[
    [Optional[list[protocols.AbstractPaymentMethod]]],
    protocols.AbstractRepository,
]:

    @dataclass
    class FakePaymentMethodRepository:
        units: list[protocols.AbstractPaymentMethod]

        def add(self, data: protocols.AbstractDraftPaymentMethod) -> protocols.AbstractPaymentMethod:
            payment_method = domain.PaymentMethod(
                id=uuid.uuid4(),
                created_at=datetime.now(),
                payment_attempt=data.payment_attempt,
                confirmable=data.confirmable,
                token=data.token,
                payment_operations=[],
            )
            self.units.append(payment_method)
            return payment_method

        def get(self, id: uuid.UUID) -> protocols.AbstractPaymentMethod:
            for unit in self.units:
                if unit.id == id:
                    return unit
            raise domain.PaymentMethod.DoesNotExist

    assert issubclass(FakePaymentMethodRepository, protocols.AbstractRepository)

    def build_repository(
        units: Optional[list[protocols.AbstractPaymentMethod]] = None,
    ) -> protocols.AbstractRepository:
        return FakePaymentMethodRepository(units=units if units else [])

    return build_repository


@pytest.fixture(scope="module")
def fake_payment_operations_repository() -> Callable[
    [Optional[list[protocols.AbstractPaymentOperation]]],
    protocols.AbstractRepository,
]:

    @dataclass
    class FakePaymentOperationRepository:
        units: list[protocols.AbstractPaymentOperation]

        def add(
            self,
            payment_method: protocols.AbstractPaymentMethod,
            type: OperationTypeEnum,
            status: OperationStatusEnum,
        ) -> protocols.AbstractPaymentOperation:
            payment_operation = domain.PaymentOperation(
                type=type,
                status=status,
                payment_method_id=payment_method.id,
            )
            payment_method.payment_operations.append(payment_operation)
            return payment_operation

        def get(  # type:ignore[empty-body]
            self, id: uuid.UUID
        ) -> protocols.AbstractPaymentOperation: ...

    assert issubclass(FakePaymentOperationRepository, protocols.AbstractRepository)

    def build_repository(
        units: Optional[list[protocols.AbstractPaymentOperation]] = None,
    ) -> protocols.AbstractRepository:
        return FakePaymentOperationRepository(units=units if units else [])

    return build_repository
