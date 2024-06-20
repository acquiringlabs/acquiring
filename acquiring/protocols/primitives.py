from typing import NewType
from uuid import UUID


ExistingPaymentMethodId = NewType("ExistingPaymentMethodId", UUID)
ExistingPaymentAttemptId = NewType("ExistingPaymentAttemptId", UUID)
