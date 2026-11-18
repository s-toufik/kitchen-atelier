from typing import Protocol, runtime_checkable

from kitchen_atelier.domain.recipe.recipe import Recipe
from kitchen_atelier.domain.recipe.recipe_draft import RecipeDraft


@runtime_checkable
class CreateRecipePort(Protocol):
    async def handle(self, draft: RecipeDraft) -> Recipe: ...
