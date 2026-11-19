from collections.abc import Callable

from fastapi import APIRouter, HTTPException, Query

from bootstrap.application.fastapi.schema.create_ingredient_request_schema import (
    CreateIngredientRequestSchema,
)
from bootstrap.application.fastapi.schema.ingredient_schema import (
    IngredientListSchema,
    IngredientSchema,
)
from kitchen_atelier.application.port.inbound.get_ingredient_port import GetIngredientPort
from kitchen_atelier.application.port.inbound.get_or_create_ingredient_port import (
    GetOrCreateIngredientPort,
)
from kitchen_atelier.application.port.inbound.list_ingredients_port import ListIngredientsPort
from kitchen_atelier.application.port.inbound.search_ingredients_port import (
    SearchIngredientsPort,
)

INGREDIENT_TAG: str = "Ingredients"
INGREDIENTS_PATH: str = "/v1/ingredients"
INGREDIENT_PATH: str = "/v1/ingredients/{ciqual_code}"


def ingredient_router(
    search_ingredients: Callable[[], SearchIngredientsPort],
    list_ingredients: Callable[[], ListIngredientsPort],
    get_or_create_ingredient: Callable[[], GetOrCreateIngredientPort],
    get_ingredient: Callable[[], GetIngredientPort],
) -> APIRouter:
    router = APIRouter(tags=[INGREDIENT_TAG])

    @router.get(INGREDIENTS_PATH)
    async def list_or_search(
        query: str | None = Query(default=None),
        limit: int = Query(default=20, ge=1, le=200),
        offset: int = Query(default=0, ge=0),
    ) -> IngredientListSchema:
        if query:
            ingredients = await search_ingredients().handle(query, limit)
        else:
            ingredients = await list_ingredients().handle(limit, offset)
        return IngredientListSchema.from_domain(ingredients)

    @router.post(INGREDIENTS_PATH, status_code=201)
    async def create(request: CreateIngredientRequestSchema) -> IngredientSchema:
        ingredient = await get_or_create_ingredient().handle(
            request.name_fr,
            request.kcal_per_100g,
            request.protein_per_100g,
            request.carb_per_100g,
            request.fat_per_100g,
        )
        return IngredientSchema.from_domain(ingredient)

    @router.get(INGREDIENT_PATH)
    async def get(ciqual_code: str) -> IngredientSchema:
        ingredient = await get_ingredient().handle(ciqual_code)
        if ingredient is None:
            raise HTTPException(status_code=404, detail="Ingredient not found")
        return IngredientSchema.from_domain(ingredient)

    return router
