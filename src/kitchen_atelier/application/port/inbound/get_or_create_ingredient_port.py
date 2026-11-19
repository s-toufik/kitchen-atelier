from typing import Protocol, runtime_checkable

from kitchen_atelier.domain.ingredient.food import Food


@runtime_checkable
class GetOrCreateIngredientPort(Protocol):
    async def handle(
        self,
        name_fr: str,
        kcal_per_100g: float,
        protein_per_100g: float,
        carb_per_100g: float,
        fat_per_100g: float,
    ) -> Food: ...
