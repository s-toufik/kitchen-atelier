from datetime import UTC, datetime
from uuid import uuid4

from kitchen_atelier.application.port.outbound.ingredient_repository_port import (
    IngredientRepository,
)
from kitchen_atelier.domain.ingredient.ingredient import Ingredient, normalize_search

CUSTOM_SOURCE: str = "custom"


class GetOrCreateIngredient:
    def __init__(self, repository: IngredientRepository) -> None:
        self._repository = repository

    async def handle(
        self,
        name_fr: str,
        kcal_per_100g: float,
        protein_per_100g: float,
        carb_per_100g: float,
        fat_per_100g: float,
    ) -> Ingredient:
        name_search = normalize_search(name_fr)
        existing = await self._repository.get_by_name(name_search)
        if existing is not None:
            return existing

        ingredient = Ingredient(
            ciqual_code=f"custom:{uuid4().hex[:12]}",
            name_fr=name_fr.strip(),
            name_search=name_search,
            kcal_per_100g=max(0.0, kcal_per_100g),
            protein_per_100g=max(0.0, protein_per_100g),
            carb_per_100g=max(0.0, carb_per_100g),
            fat_per_100g=max(0.0, fat_per_100g),
            source=CUSTOM_SOURCE,
            updated_at=datetime.now(UTC),
        )
        await self._repository.upsert_many([ingredient])
        return ingredient
