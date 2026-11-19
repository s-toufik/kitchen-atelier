from typing import Protocol, runtime_checkable

from kitchen_atelier.domain.ingredient.food import Food


@runtime_checkable
class GetIngredientPort(Protocol):
    async def handle(self, ciqual_code: str) -> Food | None: ...
