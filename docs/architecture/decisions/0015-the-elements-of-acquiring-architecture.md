# 15. The Elements of Acquiring Architecture

Date: 2024-05-30

Supercedes [8. Domain Logic happens in native Python](0008-domain-logic-happens-in-native-python.md)

## Breakdown of the Main Ideas behind Acquiring

Acquiring's Architecture is founded on 7 Founding Principles:

- Composition over Inheritance
- Local Reasoning
- Mutual Exclusion with Wide Events
- Persistence Ignorance
- Append-only Storage
- Structural Subtyping
- Taxonomy Driven Design

They are described in more detail below.

### Composition over Inheritance
From [Subclassing, Composition, Python, and You](https://www.youtube.com/watch?v=2qpW1-7TnzA).

Inheritance is about hidding information. It's a design choice that simplifies the view of an entity, omiting unimportant
details.

Inheritance is useful because it makes it easier for us to think about and manipulate complex things.

The problem is, there is very little unimportant details in payment orchestration. As a result, inheritance is a bad
design choice.

The answer is Composition.

### Local Reasoning
From [Out of the Tar Pit](https://curtclifton.net/papers/MoseleyMarks06a.pdf) 

The lack of local reasoning is the the biggest obstacle to the ongoing maintenance of software systems.

With the phrase “local reasoning”, I’m referring to the ability to understand the behavior of a piece of code by
looking at it on its own, without recourse to other parts of the system.

You know, [7 plus and minus 2](https://en.wikipedia.org/wiki/The_Magical_Number_Seven,_Plus_or_Minus_Two) things in your
working memory and all that.

The biggest factor causing a lack of local reasoning is the mishandling of state.

Programming language paradigms deal with the trade-offs imposed by state differently.

In Object Oriented Programming (OOP), state is handled in inheritance style: by hiding it. In Functional Programming (FP),
state is handled in composition style: by pushing it somewhere else.

What I mean is that using functions, rather than classes, as your primary means of handling logic forces you to think in
terms of inputs and ouputs. In the end, what you get is referential transparency — the same inputs unequivocally lead to
the same outputs. Everything which can possibly affect the result in any way is always present in the function's
parameters and its body.

That's something you don't have with OOP.

Python is not an FP language per se. Nor is it OOP. Therefore, we can use the tenets of FP wherever possible, even if we
use classes as building blocks of the architecture.

But we can be certain that this is possible if we remove any dependency whatsoever of any particular framework or library
when we deal with domain logic.

When we talk business, we will express it in pure Python, and nothing else.

### Mutual Exclusion with Wide Events
From [All you need is Wide Events, not “Metrics, Logs and Traces”](https://isburmistrov.substack.com/p/all-you-need-is-wide-events-not-metrics) and [Pyments: How To Design Payment Applications In Python](https://www.youtube.com/watch?v=2o4RgvXcYVw).

You shouldn't trust payment providers. Their trade-offs are not yours, and you have no control over their decisions.

Everything that happens in acquiring is recorded. For example, a PaymentMethod is associated with the following
wide events:
- `PaymentOperation`s record the history of a `PaymentMethod` throughout the operation types.
- `BlockEvent`s record the history of a `PaymentMethod` during the execution of every `Block`'s `run` method.
- `Transaction`s record the interaction with third party providers.

These are all Wide Events.

Wide Events are just a collection of fields with names and values, pretty much like a JSON document. Data analysts can
use it for traceability, of course, but we can use it for something more interesting: mutual exclusion.

Payment providers are designed with `at least once delivery` mechanisms. Our system gets notified of payments going
through more than once!

To prevent double charges, before running the Blocks, the system creates a `PaymentOperation` with status `started`. In
this manner, we can implement [decision logic](acquiring/domain/decision_logic.py), a set of functions that let in or bounce out instances of `PaymentMethod` running in parallel in the system.

That is a domain-driven mutual exclusion mechanism.

### Persistence Ignorance
From [Cosmic Python](https://www.cosmicpython.com/book/chapter_02_repository.html#_inverting_the_dependency_orm_depends_on_model).

Persistence Ignorance is the idea that inverting the traditional dependency where the domain depends on the ORM achieves
an implementation of the domain that stays "pure" and free from infrastructure concerns.

### Append-only Storage

Appending is generally a very efficient operation in most databases. It is also very easy to understand, and fits nicely
with functional programming, because it makes it easier to turn entities in the domain immutable.

No need to update any row if Repositories only implement `get` and `add` methods.

### Structural Subtyping (Protocols)
From [PEP 544 – Protocols: Structural subtyping (static duck typing)](https://peps.python.org/pep-0544/).

Most Python programmers know about the [abc](https://docs.python.org/3/library/abc.html) module. You have a class that
inherits from `abc.ABC`, you decorate some of its methods with `abc.abstractmethod`, and that's how you get a protocol,
which specifies type metadata for static type checkers and other third party tools. In the end, what you get is
a stronger type system, becaues it makes the data structures involved more precise.

Let us call a class that inherits from an Abstract Base Class an explicit subclass of the protocol.

The problem with them is that a class has to be explicitly marked to support them, which is counter to what idiomatic
dynamically typed Python code looks like.

How can you make a class compatible with a protocol while avoiding explicit inheritance?

With [Protocols](https://peps.python.org/pep-0544/). Let us call a class that does not inherit from an abc.ABC, but is
compatible with a class defined with `typing.Protocol`, an implicit subclass of the protocol.

If a class has the same attributes and the same methods than the protocol class, then things like `isinstance` would
work as if it inherited from an ABC class.

Structural subtyping is natural for Python programmers since it matches the runtime semantics of duck typing: an object
that has certain properties is treated independently of its actual runtime class.

### Taxonomy Driven Design
From [Pyments: How To Design Payment Applications In Python](https://www.youtube.com/watch?v=2o4RgvXcYVw)

A Payment is a Promise made by an Authorized Party.

I chose those words carefully because both the concepts of Promises and Authorization are actually computer science
concepts. One is related to Sync and Async communication, and the other is related to Identity Management.

And that means that we can place all payment methods along two axes: whether the customer needs to perform some action
to become an Authorized Party or not, and whether the Payment finalizes synchronously or asynchronously like Promises.

How do we make sure that both the with and without customer action flows can be supported? One possible way is to make
the `pay` method private.

the pay method can only be called in one of two ways. At initialization, where every payment goes first, the block can give us three kinds of results:

- Success, in which case the pay method gets called directly

- Failed, and the method will instead return the failed response

- And also Requires Action, which is special in the sense that it returns, but inside the response there’s some metadata
for the client to show to the customer, so that they can do whatever they have to do.

Then, if the actions are completed, some other action data will be sent in the request to another method, let’s call it
process_actions, which will be either successful, and therefore will lead to calling the pay method, or it will fail.

This is elegant because sometimes you have no idea whether the provider is going to require some action from the customer.
If you pay with a card in Europe, you’re likely to be redirected to your banking app. If not, then that rarely happens.

Usually though, the customer isn’t requested to complete the action through your system.

More often than not, the provider is the one asking the customer to complete the action in a banking app, out of your control.

What you get is a response with status pending, and will call the callback url of your choice with enough data for you
to acknowledge that the payment went through.

In order to accommodate both flows, we can split the pay method from another method called after_pay.

When you call pay, you may go immediately after to after_pay, if the flow is synchronous. And you will have to return,
and wait for the provider to call the callback url, which will trigger the after_pay method, if the flow is asynchronous.