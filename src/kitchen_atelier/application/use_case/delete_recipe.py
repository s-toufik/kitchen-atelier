from kitchen_atelier.application.port.outbound.recipe_repository_port import RecipeRepository
from kitchen_atelier.domain.recipe.exception.recipe_not_found import RecipeNotFound


class DeleteRecipe:
    def __init__(self, repository: RecipeRepository) -> None:
        self._repository = repository

    async def handle(self, recipe_id: str) -> None:
        recipe = await self._repository.get(recipe_id)
        if recipe is None:
            raise RecipeNotFound(recipe_id)
        await self._repository.delete(recipe_id)
