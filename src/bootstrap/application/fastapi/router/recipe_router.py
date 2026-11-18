from collections.abc import Callable

from fastapi import APIRouter

from bootstrap.application.fastapi.schema.recipe_draft_schema import RecipeDraftSchema
from bootstrap.application.fastapi.schema.recipe_schema import RecipeListSchema, RecipeSchema
from bootstrap.application.fastapi.schema.recipe_version_schema import (
    RecipeVersionListSchema,
    RecipeVersionSchema,
)
from bootstrap.application.fastapi.schema.save_recipe_version_request_schema import (
    SaveRecipeVersionRequestSchema,
)
from kitchen_atelier.application.port.inbound.create_recipe_port import CreateRecipePort
from kitchen_atelier.application.port.inbound.get_recipe_version_port import GetRecipeVersionPort
from kitchen_atelier.application.port.inbound.list_recipe_versions_port import (
    ListRecipeVersionsPort,
)
from kitchen_atelier.application.port.inbound.list_recipes_port import ListRecipesPort
from kitchen_atelier.application.port.inbound.save_recipe_version_port import (
    SaveRecipeVersionPort,
)

RECIPE_TAG: str = "Recipes"
RECIPES_PATH: str = "/v1/recipes"


def recipe_router(
    create_recipe: Callable[[], CreateRecipePort],
    save_recipe_version: Callable[[], SaveRecipeVersionPort],
    get_recipe_version: Callable[[], GetRecipeVersionPort],
    list_recipe_versions: Callable[[], ListRecipeVersionsPort],
    list_recipes: Callable[[], ListRecipesPort],
) -> APIRouter:
    router = APIRouter(tags=[RECIPE_TAG])

    @router.get(RECIPES_PATH)
    async def list_all() -> RecipeListSchema:
        return RecipeListSchema.from_domain(await list_recipes().handle())

    @router.post(RECIPES_PATH, status_code=201)
    async def create(draft: RecipeDraftSchema) -> RecipeSchema:
        recipe = await create_recipe().handle(draft.to_domain())
        return RecipeSchema.from_domain(recipe)

    @router.get(RECIPES_PATH + "/{recipe_id}/versions")
    async def list_versions(recipe_id: str) -> RecipeVersionListSchema:
        versions = await list_recipe_versions().handle(recipe_id)
        return RecipeVersionListSchema.from_domain(versions)

    @router.post(RECIPES_PATH + "/{recipe_id}/versions", status_code=201)
    async def save_version(
        recipe_id: str, request: SaveRecipeVersionRequestSchema
    ) -> RecipeVersionSchema:
        version = await save_recipe_version().handle(
            recipe_id, request.based_on_version, request.draft.to_domain()
        )
        return RecipeVersionSchema.from_domain(version)

    @router.get(RECIPES_PATH + "/{recipe_id}/versions/{version_number}")
    async def get_version(recipe_id: str, version_number: int) -> RecipeVersionSchema:
        version = await get_recipe_version().handle(recipe_id, version_number)
        return RecipeVersionSchema.from_domain(version)

    return router
