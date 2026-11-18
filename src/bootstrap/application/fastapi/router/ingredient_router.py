from collections.abc import Callable

from fastapi import APIRouter, Query

from bootstrap.application.fastapi.schema.ingredient_schema import IngredientListSchema
from kitchen_atelier.application.port.inbound.search_ingredients_port import (
    SearchIngredientsPort,
)

INGREDIENT_TAG: str = "Ingredients"
INGREDIENTS_PATH: str = "/v1/ingredients"


def ingredient_router(search_ingredients: Callable[[], SearchIngredientsPort]) -> APIRouter:
    router = APIRouter(tags=[INGREDIENT_TAG])

    @router.get(INGREDIENTS_PATH)
    async def search(
        q: str = Query(min_length=1), limit: int = Query(default=20, ge=1, le=100)
    ) -> IngredientListSchema:
        ingredients = await search_ingredients().handle(q, limit)
        return IngredientListSchema.from_domain(ingredients)

    return router
