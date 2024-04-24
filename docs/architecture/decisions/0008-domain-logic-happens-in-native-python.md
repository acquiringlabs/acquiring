# 8. Domain Logic happens in native Python

Date: 2024-04-24

## Domain, Storage, Protocols.

From [Subclassing, Composition, Python, and You](https://www.youtube.com/watch?v=2qpW1-7TnzA), by Hynek Schlawack, and
[Learning the ropes: understanding Python generics](https://www.youtube.com/watch?v=PmgHNls70eQ), by David Seddon.

Something common to every successful project I've worked in was a rich domain model that informed the current design of
the codebase and its future changes.

[A program is not its source code](https://gwern.net/doc/cs/algorithm/#naur-1985-section)

When it comes to the implementation, I've decided to avoid any third party library to express anything related to the
payments domain. No `money` library, for example. To make that more visible, imports from third party libraries are
module imports.

When it comes to the architecture, I've separated the `domain` folder from a `storage` folder where everything related
to database I/O is defined, and from a `protocols` folder where the specifics of the type system are isolated from how
everything gets implemented. [Dataclasses are hence first class citizens](https://glyph.twistedmatrix.com/2016/08/attrs.html),
and types express intent without mixing in with how that intent is implemented.

My first realization when I began with this approach was that
[`acquiring` stopped being a django-specific library](https://github.com/acquiringlabs/django-acquiring). It can support
SQLAlchemy and any other ORM out there. To the best of my knowledge, `acquiring` is the first Python library able to
support Flask, Django and FastAPI out of the box. Any Web development framework, really.

The second one was that separating the domain logic (`/domain`) from the intent expressed by types (`/protocols`) is key
to building a Protocol library, rather than an API. In other words, each component of the implementation can be replaced
by a different one, as long as it respects the boundaries imposed by the interfaces.

This is the point where `acquiring`'s design and [Cosmic Python](https://www.cosmicpython.com/)'s diverge. Persistence
ignorance separates domain from storage. But duck typing allows me to build a Protocol.
