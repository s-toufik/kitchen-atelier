from datetime import UTC, datetime
from decimal import Decimal
from uuid import uuid4

from kitchen_atelier.application.port.outbound.ingredient_repository_port import (
    IngredientRepository,
)
from kitchen_atelier.domain.ingredient.energy import Energy
from kitchen_atelier.domain.ingredient.fatty_acids import FattyAcids
from kitchen_atelier.domain.ingredient.food import Food
from kitchen_atelier.domain.ingredient.food_classification import FoodClassification
from kitchen_atelier.domain.ingredient.food_identity import FoodIdentity
from kitchen_atelier.domain.ingredient.macronutrients import Macronutrients
from kitchen_atelier.domain.ingredient.minerals import Minerals
from kitchen_atelier.domain.ingredient.normalize_search import normalize_search
from kitchen_atelier.domain.ingredient.nutritional_composition import NutritionalComposition
from kitchen_atelier.domain.ingredient.sugars import Sugars
from kitchen_atelier.domain.ingredient.vitamins import Vitamins

CUSTOM_SOURCE: str = "custom"
_NO_CLASSIFICATION = FoodClassification("", "", "", "", "", "")


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
    ) -> Food:
        name_search = normalize_search(name_fr)
        existing = await self._repository.get_by_name(name_search)
        if existing is not None:
            return existing

        food = Food(
            identity=FoodIdentity(ciqual_code=f"custom:{uuid4().hex[:12]}", name=name_fr.strip()),
            classification=_NO_CLASSIFICATION,
            nutrition=NutritionalComposition(
                energy=Energy(regulation_1169_kcal=_non_negative(kcal_per_100g)),
                macronutrients=Macronutrients(
                    protein_jones_g=_non_negative(protein_per_100g),
                    carbohydrates_g=_non_negative(carb_per_100g),
                    fat_g=_non_negative(fat_per_100g),
                ),
                sugars=Sugars(),
                fatty_acids=FattyAcids(),
                minerals=Minerals(),
                vitamins=Vitamins(),
            ),
            source=CUSTOM_SOURCE,
            source_version="",
            updated_at=datetime.now(UTC),
        )
        await self._repository.upsert_many([food])
        return food


def _non_negative(value: float) -> Decimal:
    return Decimal(str(max(0.0, value)))
