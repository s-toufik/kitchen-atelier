from typing import Protocol, runtime_checkable

from kitchen_atelier.domain.recipe.recipe import Recipe
from kitchen_atelier.domain.recipe.recipe_version import RecipeVersion


@runtime_checkable
class RecipeRepository(Protocol):
    async def get(self, recipe_id: str) -> Recipe | None: ...

    async def list_recipes(self) -> list[Recipe]: ...

    async def get_version(self, recipe_id: str, version_number: int) -> RecipeVersion | None: ...

    async def list_versions(self, recipe_id: str) -> list[RecipeVersion]: ...

    async def save(self, recipe: Recipe, version: RecipeVersion) -> None: ...
