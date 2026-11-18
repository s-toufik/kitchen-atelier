from collections.abc import Iterable
from typing import Protocol, runtime_checkable

from kitchen_atelier.domain.ingredient.ingredient import Ingredient


@runtime_checkable
class IngredientRepository(Protocol):
    async def search(self, query: str, limit: int = 20) -> list[Ingredient]: ...

    async def get(self, ciqual_code: str) -> Ingredient | None: ...

    async def get_by_name(self, name_search: str) -> Ingredient | None: ...

    async def list_all(self, limit: int = 50, offset: int = 0) -> list[Ingredient]: ...

    async def upsert_many(self, ingredients: Iterable[Ingredient]) -> int: ...
