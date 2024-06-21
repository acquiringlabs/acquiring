# 16. PaymentAttempt vs PaymentMethod

Date: 2024-06-21

## What gets paid goes through Milestones. How it gets paid goes through Events.

PaymentAttempt is the main point of interaction with the acquiring library. Its primary key column is meant to be
the foreign key for the "Order" in the main application (or whatever its name is).

A PaymentAttempt goes through multiple Milestones as it gets a PaymentMethod, it gets completed, and potentially
voided or refunded (See [ADR 0013](/architecture/decisions/0013-separate-void-and-refund-operation-types)). Potentially,
a new PaymentMethod can be added, in case the first failed.

From the moment a PaymentMethod gets added, it goes through its own lifecycle. As it goes through
each operation type, it gets OperationEvents attached to it (as well as BlockEvents).

The What (PaymentAttempt) and the How (PaymentMethod) go through independent lifecycles, and therefore must be represented
by different entities.

A PaymentAttempt, though, is not the same as the Order. It represents What gets paid, but the fulfilling of the payment
and the fulfilling of the Order are, too, independent state flows.

Orders have PaymentAttempts, they're not the same.