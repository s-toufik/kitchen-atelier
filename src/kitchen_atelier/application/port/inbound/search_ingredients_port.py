from typing import Protocol, runtime_checkable

from kitchen_atelier.domain.ingredient.food import Food


@runtime_checkable
class SearchIngredientsPort(Protocol):
    async def handle(self, query: str, limit: int = 20) -> list[Food]: ...
