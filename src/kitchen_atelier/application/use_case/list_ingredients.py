from kitchen_atelier.application.port.outbound.ingredient_repository_port import (
    IngredientRepository,
)
from kitchen_atelier.domain.ingredient.ingredient import Ingredient


class ListIngredients:
    def __init__(self, repository: IngredientRepository) -> None:
        self._repository = repository

    async def handle(self, limit: int = 50, offset: int = 0) -> list[Ingredient]:
        return await self._repository.list_all(limit, offset)
