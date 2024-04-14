# 6. Use import module more often than from module import

Date: 2024-04-14

## Namespaces are one honking great idea

From Stack Overflow's [Use 'import module' or 'from module import'?](https://stackoverflow.com/questions/710551/use-import-module-or-from-module-import)

In this project, you can import `PaymentMethod` from several files:

- acquiring/domain/payments.py
- acquiring/models/django.py
- acquiring/protocols/payments.py
- ...

They're often used in combination: models/django.py `PaymentMethod`'s `to_domain` is annotated
with protocols/payments.py `PaymentMethod` and returns an instance of domain/payments.py `PaymentMethod`.

That sentence alone should make it clear that [name collision](https://en.wikipedia.org/wiki/Naming_collision) is a
potential problem. So how do we deal with that?

How about this:

```python
from acquiring.domain.payments import PaymentMethod as DomainPaymentMethod
from acquiring.models import PaymentMethod as ModelPaymentMethod
from acquiring.protocols import PaymentMethod as ProtocolPaymentMethod
```

This is not a bad approach. It works.

The problem with this is twofold. First, it's very hard to keep this naming consistent. The `as` statement makes naming
very flexible. It makes hard for programmers to track which class are you using. And nothing prevents me from carelessly
assigning an incorrect name, as in `from acquiring.models import PaymentMethod as DomainPaymentMethod`.

But second, this is [homeopathic naming](https://kevlinhenney.medium.com/exceptional-naming-6e3c8f5bffac):

> Homeopathic naming is one of the commonest habits programmers can fall into without realising: making names longer by
> adding more words with the goal of adding more meaning to code, but in practice diluting the meaning.

I really love this concept. I also love Kevin's explanation for why this is something to be mindful of:

> Affixing Lego-brick parts to an identifier does not amplify or enhance its meaning, and often serves to highlight
> there may have been little meaning there in the first place.

Rather than prefixing `Domain` or `Model` or `Protocol` to `PaymentMethod`, what we can do is the following:

```python
from acquiring import domain, models, protocols
```

Lovely. What `PaymentMethod` can I use? `domain.PaymentMethod`, `models.PaymentMethod` or `protocols.PaymentMethod`.

This is a way cleaner, in my opinion, to make namespace explicit. I'm told it is also faster, but I can't find a
reliable source to back that up. In this project, we will therefore favor this way of bringing classes into the
namespace.

It is mostly a matter of style. But not entirely idiosyncratic.