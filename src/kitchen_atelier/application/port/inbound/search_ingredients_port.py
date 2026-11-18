from typing import Protocol, runtime_checkable

from kitchen_atelier.domain.ingredient.ingredient import Ingredient


@runtime_checkable
class SearchIngredientsPort(Protocol):
    async def handle(self, query: str, limit: int = 20) -> list[Ingredient]: ...
