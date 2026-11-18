from datetime import UTC, datetime

from kitchen_atelier.application.port.outbound.recipe_repository_port import RecipeRepository
from kitchen_atelier.domain.recipe.exception.recipe_not_found import RecipeNotFound
from kitchen_atelier.domain.recipe.exception.stale_version import StaleVersion
from kitchen_atelier.domain.recipe.recipe_draft import RecipeDraft
from kitchen_atelier.domain.recipe.recipe_version import RecipeVersion


class SaveRecipeVersion:
    """Appends the next version. Refuses to save over a version that is no longer the latest."""

    def __init__(self, repository: RecipeRepository) -> None:
        self._repository = repository

    async def handle(
        self, recipe_id: str, based_on_version: int, draft: RecipeDraft
    ) -> RecipeVersion:
        recipe = await self._repository.get(recipe_id)
        if recipe is None:
            raise RecipeNotFound(recipe_id)
        if based_on_version != recipe.current_version_number:
            raise StaleVersion(recipe_id, based_on_version, recipe.current_version_number)

        now = datetime.now(UTC)
        next_version = RecipeVersion(
            recipe_id=recipe_id,
            version_number=recipe.current_version_number + 1,
            saved_at=now,
            draft=draft,
        )
        updated_recipe = recipe.with_new_version(next_version, now)
        await self._repository.save(updated_recipe, next_version)
        return next_version
