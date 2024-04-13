# 5. Maybe Functions Considered Harmful

Date: 2024-04-13

## Functions should _do_ something, **not** _maybe do_ something.

From [Maybe Functions](https://blog.benwinding.com/maybe-functions/)

`Repository.get` is a particularly interesting function.

See, it is the place where the database is accessed to retrieve data. There are only two possible outcomes to `get`:

1. The filters specified apply to a row, and a domain object gets retrieved from the database.
2. The filters do not apply, and the database sends no errors.

While the first is straightforward, most ORMs handled the second case in two ways: they either raise an error
(e.g., calling `one()` on SQLAlchemy, or `get()` on Django), or return `None` (calling `first()` both in SQLAlchemy
and Django).

In this project, `Repository.get` *never* goes for the second option. The type system, enforced by `typing.Protocol`,
will not accept a class acting as a Repository if that class's `get` method can return None (only
`get(id: UUID) -> PaymentMethod` is allowed, and `PaymentMethod | None` is banned).

Functions that *maybe* return an object, but sometimes don't, are called Maybe Functions.
**Maybe Functions are prohibited, banned, verboten**.

This is related to the [Null Object Pattern](https://en.wikipedia.org/wiki/Null_object_pattern),
but from the perspective of functions.

Maybe functions are easier to call, because the outcome is tied to the validation. You can tell that something
went wrong by looking at the result.

The problem is that you don't know what happened. The caller can only hope that everything went well, and it wasn't
something nasty with the connection or anything like that. You can't decide what to do in the case of two error
scenarios.

Should get be retried if connection timeout? Too bad, you only have a `None` to work with, there's no way to tell if
it was a timeout!

If that isn't enough, consider this piece of code (from acquiring/domain/flow.py):

```python
try:
    payment_method = payment_method_repository.get(id=payment_method.id)
except domain.PaymentMethod.DoesNotExist:
    # handle DoesNotExist
```

This code replaces `payment_method` with the data stored in the database. As in _the only thing that matters
is in the source of truth_.

How would that look like if `payment_method_repository.get` were a Maybe Function?

```python
if (_payment_method := payment_method_repository.get(paymen_method_.id)) is None:
    # Handle None
payment_method = _payment_method
```

Clever piece of code! The assignment in the former case hasn't happened when the error is raised, and so `payment_method`
is still holding the old information by the time I'm handling the error condition.

In the second case, the assignment has already happened. So, something bad went on, and if I wanted to replace the
`payment_method` variable with the new info, the Maybe Function would have erased everything by the time I'm handling
the error. So, I have to assign the outcome of `get` to a placeholder `_payment_method`, and then replace later on
if and only if `get` didn't return `None`.

And the walrus, for goodness sake!
[What were you thinking Guido?](https://mail.python.org/pipermail/python-committers/2018-July/005664.html)

Not good.

This is lifting the maybeness up to the caller, and if functions were people, it would be very bad manners.

Maybe Functions. OK if you disagree here. But not in this codebase. Go play somewhere else. Maybe.