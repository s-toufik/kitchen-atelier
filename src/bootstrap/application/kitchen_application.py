import traceback
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from pycraftcore.web.asgi import ASGIApp
from pycraftcore.web.schema import ApiSettings

from bootstrap.application.fastapi.fastapi_api import create_fastapi_api
from bootstrap.configuration.settings import ProcessSettings
from bootstrap.container.kitchen_container import KitchenContainer
from src import APPLICATION_VERSION

ROLE: str = "kitchen-atelier"


@asynccontextmanager
async def _lifespan(container: KitchenContainer) -> AsyncGenerator[None]:
    try:
        await container.boot()
    except Exception as exception:
        container.logging.critical(
            "Kitchen container failed to boot:\n" + "".join(traceback.format_exception(exception))
        )
        raise

    try:
        yield
    finally:
        await container.stop()


def create_kitchen_application(settings: ProcessSettings | None = None) -> ASGIApp:
    process_settings = settings or ProcessSettings.for_role(ROLE)
    container = KitchenContainer(process_settings)
    server = container.server

    api = ApiSettings(
        title=server.name,
        version=APPLICATION_VERSION,
        base_path=server.base_path,
        docs=server.docs,
        cors_origins=server.cors_origins,
    )
    return create_fastapi_api(
        api,
        lifespan=lambda: _lifespan(container),
        create_recipe=lambda: container.create_recipe,
        save_recipe_version=lambda: container.save_recipe_version,
        get_recipe_version=lambda: container.get_recipe_version,
        list_recipe_versions=lambda: container.list_recipe_versions,
        list_recipes=lambda: container.list_recipes,
        search_ingredients=lambda: container.search_ingredients,
        list_ingredients=lambda: container.list_ingredients,
        get_or_create_ingredient=lambda: container.get_or_create_ingredient,
        actuator=container.actuator,
        logger=container.logging,
    )
