from typing import Protocol, runtime_checkable

from kitchen_atelier.domain.recipe.recipe_draft import RecipeDraft
from kitchen_atelier.domain.recipe.recipe_version import RecipeVersion


@runtime_checkable
class SaveRecipeVersionPort(Protocol):
    async def handle(self, recipe_id: str, based_on_version: int, draft: RecipeDraft) -> RecipeVersion: ...
