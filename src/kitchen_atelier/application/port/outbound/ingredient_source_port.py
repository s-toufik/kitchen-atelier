from typing import Protocol, runtime_checkable

from kitchen_atelier.domain.ingredient.ingredient import Ingredient


@runtime_checkable
class IngredientSource(Protocol):
    async def fetch_all(self) -> list[Ingredient]: ...
