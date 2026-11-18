from typing import Protocol, runtime_checkable

from kitchen_atelier.domain.recipe.recipe_version import RecipeVersion


@runtime_checkable
class ListRecipeVersionsPort(Protocol):
    async def handle(self, recipe_id: str) -> list[RecipeVersion]: ...
