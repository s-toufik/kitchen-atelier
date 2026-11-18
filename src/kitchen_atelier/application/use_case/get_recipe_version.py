from kitchen_atelier.application.port.outbound.recipe_repository_port import RecipeRepository
from kitchen_atelier.domain.recipe.exception.recipe_version_not_found import (
    RecipeVersionNotFound,
)
from kitchen_atelier.domain.recipe.recipe_version import RecipeVersion


class GetRecipeVersion:
    def __init__(self, repository: RecipeRepository) -> None:
        self._repository = repository

    async def handle(self, recipe_id: str, version_number: int) -> RecipeVersion:
        version = await self._repository.get_version(recipe_id, version_number)
        if version is None:
            raise RecipeVersionNotFound(recipe_id, version_number)
        return version
