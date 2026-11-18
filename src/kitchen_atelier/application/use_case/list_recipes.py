from kitchen_atelier.application.port.outbound.recipe_repository_port import RecipeRepository
from kitchen_atelier.domain.recipe.recipe import Recipe


class ListRecipes:
    def __init__(self, repository: RecipeRepository) -> None:
        self._repository = repository

    async def handle(self) -> list[Recipe]:
        recipes = await self._repository.list_recipes()
        return sorted(recipes, key=lambda recipe: recipe.updated_at, reverse=True)
