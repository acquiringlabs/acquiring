# 13. Separate Void and Refund operation types

Date: 2024-05-26

## Reversing a Payment should follow the same structure as making the payment

After much consideration, I decided that it makes more sense to separate void from refund than keeping them together.

I've worked on systems where this separation isn't clear, and it wasn't earth shattering. But the explosion of payment
methods means that separating void from refund could be a good choice given that:

- Decision logic on when to void and refund depends on the `PaymentSaga` (can this payment be voided?) and the payment
method itself (has this payment been captured?).
    - Answering the first question can be done by configuring the blocks given to PaymentSaga itself. If there is no `void_block`, then
it can be assumed that it does not support void, and only refund is possible.
    - The second question can be answered with the `payment operations` associated with the paymentmethod. If there are
payment operation with type after_pay and status completed, then it can be voided, unless there is one with type capture.
- The structure reflects that of pay and capture. Revering a payment in dual message mode should look a lot like making
that payment. `Pay + Capture - Refund = Pay - Void`, so to say.

The structure of the void method will be slightly different than the others, but that can be arranged with a decorator
which checks for the void_block before any query is made to the database to refresh the payment.

### What we get

This results in something extremely neat, which is that the logic that has to do with deciding whether to void or refund
is placed on the structure of the `PaymentSaga`. It is consistent, it doesn't have to be duplicated across blocks that belong
to different `PaymentSaga` strategies, and it leaves the blocks to do what they are meant to do anyways.