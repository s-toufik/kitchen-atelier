from collections.abc import Iterable
from datetime import UTC, datetime

from kitchen_atelier.domain.ingredient.ingredient import Ingredient, normalize_search
from kitchen_atelier.domain.recipe.recipe import Recipe
from kitchen_atelier.domain.recipe.recipe_version import RecipeVersion


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
) -> Ingredient:
    return Ingredient(
        ciqual_code=ciqual_code,
        name_fr=name_fr,
        name_search=normalize_search(name_fr),
        kcal_per_100g=kcal_per_100g,
        protein_per_100g=protein_per_100g,
        carb_per_100g=carb_per_100g,
        fat_per_100g=fat_per_100g,
        source=source,
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
        self.by_code: dict[str, Ingredient] = {}

    async def search(self, query: str, limit: int = 20) -> list[Ingredient]:
        matches = [
            ingredient
            for ingredient in self.by_code.values()
            if query in ingredient.name_search
        ]
        return matches[:limit]

    async def get(self, ciqual_code: str) -> Ingredient | None:
        return self.by_code.get(ciqual_code)

    async def get_by_name(self, name_search: str) -> Ingredient | None:
        for ingredient in self.by_code.values():
            if ingredient.name_search == name_search:
                return ingredient
        return None

    async def list_all(self, limit: int = 50, offset: int = 0) -> list[Ingredient]:
        ordered = sorted(self.by_code.values(), key=lambda ingredient: ingredient.name_fr)
        return ordered[offset : offset + limit]

    async def upsert_many(self, ingredients: Iterable[Ingredient]) -> int:
        changed = 0
        for ingredient in ingredients:
            existing = self.by_code.get(ingredient.ciqual_code)
            if existing is None or existing != ingredient:
                changed += 1
            self.by_code[ingredient.ciqual_code] = ingredient
        return changed


class FakeIngredientSource:
    def __init__(self, ingredients: list[Ingredient]) -> None:
        self._ingredients = ingredients

    async def fetch_all(self) -> list[Ingredient]:
        return self._ingredients
