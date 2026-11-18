from collections.abc import Iterable

from kitchen_atelier.domain.ingredient.ingredient import Ingredient
from kitchen_atelier.domain.recipe.recipe import Recipe
from kitchen_atelier.domain.recipe.recipe_version import RecipeVersion


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
