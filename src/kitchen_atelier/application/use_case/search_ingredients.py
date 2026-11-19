from kitchen_atelier.application.port.outbound.ingredient_repository_port import (
    IngredientRepository,
)
from kitchen_atelier.domain.ingredient.food import Food
from kitchen_atelier.domain.ingredient.normalize_search import normalize_search


class SearchIngredients:
    def __init__(self, repository: IngredientRepository) -> None:
        self._repository = repository

    async def handle(self, query: str, limit: int = 20) -> list[Food]:
        normalized = normalize_search(query)
        if not normalized:
            return []
        return await self._repository.search(normalized, limit)
