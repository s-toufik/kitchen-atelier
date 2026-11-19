from typing import Protocol, runtime_checkable

from kitchen_atelier.domain.ingredient.food import Food


@runtime_checkable
class ListIngredientsPort(Protocol):
    async def handle(self, limit: int = 50, offset: int = 0) -> list[Food]: ...
