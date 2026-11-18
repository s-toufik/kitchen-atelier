from typing import Protocol, runtime_checkable

from kitchen_atelier.domain.ingredient.ingredient import Ingredient


@runtime_checkable
class ListIngredientsPort(Protocol):
    async def handle(self, limit: int = 50, offset: int = 0) -> list[Ingredient]: ...
