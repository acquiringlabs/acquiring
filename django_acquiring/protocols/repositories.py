from typing import Protocol, runtime_checkable
from uuid import UUID


@runtime_checkable
class AbstractRepository(Protocol):

    def add(self, *args, **kwargs): ...

    def get(self, id: UUID): ...
