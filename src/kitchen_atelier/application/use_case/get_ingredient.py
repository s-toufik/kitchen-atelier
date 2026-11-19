from kitchen_atelier.application.port.outbound.ingredient_repository_port import (
    IngredientRepository,
)
from kitchen_atelier.domain.ingredient.food import Food


class GetIngredient:
    def __init__(self, repository: IngredientRepository) -> None:
        self._repository = repository

    async def handle(self, ciqual_code: str) -> Food | None:
        return await self._repository.get(ciqual_code)
