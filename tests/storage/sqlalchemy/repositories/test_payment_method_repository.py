from datetime import datetime, timezone

import pytest
from faker import Faker

from acquiring import utils

fake = Faker()

if utils.is_sqlalchemy_installed():
    from tests.storage.sqlalchemy.factories import PaymentAttemptFactory


@pytest.mark.skip(reason="Work in progress")
def test_sqlalchemyFactoriesWorkProperly() -> None:
    PaymentAttemptFactory(created_at=datetime.now(timezone.utc))
