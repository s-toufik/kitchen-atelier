from collections.abc import Iterable
from typing import Protocol, runtime_checkable

from kitchen_atelier.domain.ingredient.food import Food


@runtime_checkable
class IngredientRepository(Protocol):
    async def search(self, query: str, limit: int = 20) -> list[Food]: ...

    async def get(self, ciqual_code: str) -> Food | None: ...

    async def get_by_name(self, name_search: str) -> Food | None: ...

    async def list_all(self, limit: int = 50, offset: int = 0) -> list[Food]: ...

    async def upsert_many(self, foods: Iterable[Food]) -> int: ...
