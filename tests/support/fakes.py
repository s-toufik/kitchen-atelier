from collections.abc import Iterable
from datetime import UTC, datetime
from decimal import Decimal

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
from kitchen_atelier.domain.recipe.recipe import Recipe
from kitchen_atelier.domain.recipe.recipe_version import RecipeVersion

_NO_CLASSIFICATION = FoodClassification("", "", "", "", "", "")


def make_ingredient(
    ciqual_code: str = "1",
    name_fr: str = "Riz",
    *,
    kcal_per_100g: float = 130,
    protein_per_100g: float = 2.7,
    carb_per_100g: float = 28.0,
    fat_per_100g: float = 0.3,
    source: str = "ciqual",
    updated_at: datetime | None = None,
) -> Food:
    return Food(
        identity=FoodIdentity(ciqual_code=ciqual_code, name=name_fr),
        classification=_NO_CLASSIFICATION,
        nutrition=NutritionalComposition(
            energy=Energy(regulation_1169_kcal=Decimal(str(kcal_per_100g))),
            macronutrients=Macronutrients(
                protein_jones_g=Decimal(str(protein_per_100g)),
                carbohydrates_g=Decimal(str(carb_per_100g)),
                fat_g=Decimal(str(fat_per_100g)),
            ),
            sugars=Sugars(),
            fatty_acids=FattyAcids(),
            minerals=Minerals(),
            vitamins=Vitamins(),
        ),
        source=source,
        source_version="Ciqual 2020" if source == "ciqual" else "",
        updated_at=updated_at or datetime.now(UTC),
    )


class FakeRecipeRepository:
    def __init__(self) -> None:
        self.recipes: dict[str, Recipe] = {}
        self.versions: dict[tuple[str, int], RecipeVersion] = {}

    async def get(self, recipe_id: str) -> Recipe | None:
        return self.recipes.get(recipe_id)

    async def list_recipes(self) -> list[Recipe]:
        return list(self.recipes.values())

    async def get_version(self, recipe_id: str, version_number: int) -> RecipeVersion | None:
        return self.versions.get((recipe_id, version_number))

    async def list_versions(self, recipe_id: str) -> list[RecipeVersion]:
        return [
            version
            for (recipe_id_key, _), version in self.versions.items()
            if recipe_id_key == recipe_id
        ]

    async def save(self, recipe: Recipe, version: RecipeVersion) -> None:
        self.versions[(version.recipe_id, version.version_number)] = version
        self.recipes[recipe.id] = recipe


class FakeIngredientRepository:
    def __init__(self) -> None:
        self.by_code: dict[str, Food] = {}

    async def search(self, query: str, limit: int = 20) -> list[Food]:
        matches = [
            food for food in self.by_code.values() if query in normalize_search(food.identity.name)
        ]
        return matches[:limit]

    async def get(self, ciqual_code: str) -> Food | None:
        return self.by_code.get(ciqual_code)

    async def get_by_name(self, name_search: str) -> Food | None:
        for food in self.by_code.values():
            if normalize_search(food.identity.name) == name_search:
                return food
        return None

    async def list_all(self, limit: int = 50, offset: int = 0) -> list[Food]:
        ordered = sorted(self.by_code.values(), key=lambda food: food.identity.name)
        return ordered[offset : offset + limit]

    async def upsert_many(self, foods: Iterable[Food]) -> int:
        changed = 0
        for food in foods:
            existing = self.by_code.get(food.identity.ciqual_code)
            if existing is None or existing != food:
                changed += 1
            self.by_code[food.identity.ciqual_code] = food
        return changed


class FakeIngredientSource:
    def __init__(self, foods: list[Food]) -> None:
        self._foods = foods

    async def fetch_all(self) -> list[Food]:
        return self._foods
