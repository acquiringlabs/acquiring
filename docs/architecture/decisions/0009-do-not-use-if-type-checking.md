# 9. Do Not Use `if TYPE_CHECKING`

Date: 2024-04-25

From: [Why if TYPE_CHECKING](https://vickiboykis.com/2023/12/11/why-if-type_checking/), by Vicki Boykis

## Be very careful when using type annotations

Most people would be shocked to [find out](https://twitter.com/charliermarsh/status/1733865143694487769) that this piece
of code FAILS:

```python
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Sequence

def func(value: Sequence[int]) -> None:
    pass
```

The core thesis is this: **types are very broad hints and sometimes lies**. This is the result of trying to
[gradually type](https://wphomes.soic.indiana.edu/jsiek/what-is-gradual-typing/) Python, a dynamically-typed language.

mypy does is basically start by analyzing your code module-by-module, keeping track of each new class/type that’s
being defined. During this process, if mypy sees a type hint using a type that hasn’t been defined yet, it will
substitute it with a placeholder type.

`if TYPE_CHECKING` is a hack to make mypy work with circular dependencies. What we need, then, is to decouple the type
system from the domain logic. Therefore, `TYPE_CHECKING` is pointless once we've separated `domain` from `protocols`.

Understand: Python's type-checking is there to reveal the writer's intent to the reader, and nothing else.
