from collections.abc import AsyncGenerator, Callable
from contextlib import AbstractAsyncContextManager, asynccontextmanager

from fastapi import FastAPI
from fastapi.routing import APIRoute, iter_route_contexts
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from pycraftcore.logger.port import Logger
from pycraftcore.web.actuator import ACTUATOR_PATH, Actuator
from pycraftcore.web.schema import ApiSettings
from pycraftcore.web_fastapi import actuator_router, create_app, detail_handler

from bootstrap.application.fastapi.router.ingredient_router import ingredient_router
from bootstrap.application.fastapi.router.recipe_router import recipe_router
from kitchen_atelier.application.port.inbound.create_recipe_port import CreateRecipePort
from kitchen_atelier.application.port.inbound.get_recipe_version_port import GetRecipeVersionPort
from kitchen_atelier.application.port.inbound.list_recipe_versions_port import (
    ListRecipeVersionsPort,
)
from kitchen_atelier.application.port.inbound.list_recipes_port import ListRecipesPort
from kitchen_atelier.application.port.inbound.save_recipe_version_port import (
    SaveRecipeVersionPort,
)
from kitchen_atelier.application.port.inbound.search_ingredients_port import (
    SearchIngredientsPort,
)
from kitchen_atelier.domain.recipe.exception.recipe_not_found import RecipeNotFound
from kitchen_atelier.domain.recipe.exception.recipe_version_not_found import (
    RecipeVersionNotFound,
)
from kitchen_atelier.domain.recipe.exception.stale_version import StaleVersion


def create_fastapi_api(
    api: ApiSettings,
    *,
    lifespan: Callable[[], AbstractAsyncContextManager[None]],
    create_recipe: Callable[[], CreateRecipePort],
    save_recipe_version: Callable[[], SaveRecipeVersionPort],
    get_recipe_version: Callable[[], GetRecipeVersionPort],
    list_recipe_versions: Callable[[], ListRecipeVersionsPort],
    list_recipes: Callable[[], ListRecipesPort],
    search_ingredients: Callable[[], SearchIngredientsPort],
    actuator: Actuator,
    logger: Logger,
) -> FastAPI:
    app: FastAPI = create_app(
        api,
        routes=[
            recipe_router(
                create_recipe,
                save_recipe_version,
                get_recipe_version,
                list_recipe_versions,
                list_recipes,
            ),
            ingredient_router(search_ingredients),
            actuator_router(actuator),
        ],
        lifespan=lambda: _logging_routes(lifespan, app, logger),
        exception_handlers={
            RecipeNotFound: detail_handler(404),
            RecipeVersionNotFound: detail_handler(404),
            StaleVersion: detail_handler(409),
        },
    )
    FastAPIInstrumentor.instrument_app(
        app, excluded_urls=ACTUATOR_PATH, exclude_spans=["receive", "send"]
    )
    return app


@asynccontextmanager
async def _logging_routes(
    lifespan: Callable[[], AbstractAsyncContextManager[None]], app: FastAPI, logger: Logger
) -> AsyncGenerator[None]:
    async with lifespan():
        for route in iter_route_contexts(app.routes):
            if isinstance(route.route, APIRoute):
                methods = " ".join(sorted(set(route.methods or ()) - {"OPTIONS", "HEAD"}))
                logger.info(f"Route {methods} {route.path} included")
        yield
