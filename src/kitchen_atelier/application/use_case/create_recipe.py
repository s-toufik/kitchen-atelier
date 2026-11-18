from datetime import UTC, datetime
from uuid import uuid4

from kitchen_atelier.application.port.outbound.recipe_repository_port import RecipeRepository
from kitchen_atelier.domain.recipe.recipe import Recipe
from kitchen_atelier.domain.recipe.recipe_draft import RecipeDraft
from kitchen_atelier.domain.recipe.recipe_version import RecipeVersion


class CreateRecipe:
    def __init__(self, repository: RecipeRepository) -> None:
        self._repository = repository

    async def handle(self, draft: RecipeDraft) -> Recipe:
        recipe_id = uuid4().hex
        now = datetime.now(UTC)
        version = RecipeVersion(recipe_id=recipe_id, version_number=1, saved_at=now, draft=draft)
        recipe = Recipe.start(recipe_id, version, now)
        await self._repository.save(recipe, version)
        return recipe
