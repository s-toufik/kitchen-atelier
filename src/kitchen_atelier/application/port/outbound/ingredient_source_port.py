from typing import Protocol, runtime_checkable

from kitchen_atelier.domain.ingredient.food import Food


@runtime_checkable
class IngredientSource(Protocol):
    async def fetch_all(self) -> list[Food]: ...
