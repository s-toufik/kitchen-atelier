from kitchen_atelier.application.port.outbound.recipe_repository_port import RecipeRepository
from kitchen_atelier.domain.recipe.exception.recipe_not_found import RecipeNotFound
from kitchen_atelier.domain.recipe.recipe_version import RecipeVersion


class ListRecipeVersions:
    def __init__(self, repository: RecipeRepository) -> None:
        self._repository = repository

    async def handle(self, recipe_id: str) -> list[RecipeVersion]:
        if await self._repository.get(recipe_id) is None:
            raise RecipeNotFound(recipe_id)
        versions = await self._repository.list_versions(recipe_id)
        return sorted(versions, key=lambda version: version.version_number, reverse=True)
