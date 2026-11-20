from functools import cached_property

from pycraftcore.application_configuration import ApplicationConfiguration
from pycraftcore.application_configuration.model.server import AsgiServer
from pycraftcore.logger.port import Logger
from pycraftcore.web.actuator import Actuator

from bootstrap.di.kitchen_di import KitchenDI
from kitchen_atelier.application.port.outbound.ingredient_repository_port import (
    IngredientRepository,
)
from kitchen_atelier.application.port.outbound.recipe_repository_port import RecipeRepository
from kitchen_atelier.application.use_case.create_recipe import CreateRecipe
from kitchen_atelier.application.use_case.delete_recipe import DeleteRecipe
from kitchen_atelier.application.use_case.get_ingredient import GetIngredient
from kitchen_atelier.application.use_case.get_or_create_ingredient import GetOrCreateIngredient
from kitchen_atelier.application.use_case.get_recipe_version import GetRecipeVersion
from kitchen_atelier.application.use_case.list_ingredients import ListIngredients
from kitchen_atelier.application.use_case.list_recipe_versions import ListRecipeVersions
from kitchen_atelier.application.use_case.list_recipes import ListRecipes
from kitchen_atelier.application.use_case.refresh_ingredient_catalog import (
    RefreshIngredientCatalog,
)
from kitchen_atelier.application.use_case.save_recipe_version import SaveRecipeVersion
from kitchen_atelier.application.use_case.search_ingredients import SearchIngredients
from src import (
    APPLICATION_AUTHORS_EMAIL,
    APPLICATION_DEPLOYMENT_ENVIRONMENT,
    APPLICATION_NAME,
    APPLICATION_VERSION,
)

SERVER_NAME: str = "kitchen-atelier"
NOT_BOOTED: str = "The kitchen container is not booted"


class KitchenContainer(KitchenDI):
    _ingredient_repository: IngredientRepository | None = None
    _recipe_repository: RecipeRepository | None = None
    _ready: bool = False

    @property
    def logging(self) -> Logger:
        return self._logging

    @property
    def application_configuration(self) -> ApplicationConfiguration:
        return self._configuration

    @property
    def server(self) -> AsgiServer:
        return self._configuration.server.asgi(SERVER_NAME)

    @cached_property
    def create_recipe(self) -> CreateRecipe:
        return CreateRecipe(_booted(self._recipe_repository))

    @cached_property
    def save_recipe_version(self) -> SaveRecipeVersion:
        return SaveRecipeVersion(_booted(self._recipe_repository))

    @cached_property
    def get_recipe_version(self) -> GetRecipeVersion:
        return GetRecipeVersion(_booted(self._recipe_repository))

    @cached_property
    def list_recipe_versions(self) -> ListRecipeVersions:
        return ListRecipeVersions(_booted(self._recipe_repository))

    @cached_property
    def list_recipes(self) -> ListRecipes:
        return ListRecipes(_booted(self._recipe_repository))

    @cached_property
    def delete_recipe(self) -> DeleteRecipe:
        return DeleteRecipe(_booted(self._recipe_repository))

    @cached_property
    def search_ingredients(self) -> SearchIngredients:
        return SearchIngredients(_booted(self._ingredient_repository))

    @cached_property
    def list_ingredients(self) -> ListIngredients:
        return ListIngredients(_booted(self._ingredient_repository))

    @cached_property
    def get_ingredient(self) -> GetIngredient:
        return GetIngredient(_booted(self._ingredient_repository))

    @cached_property
    def get_or_create_ingredient(self) -> GetOrCreateIngredient:
        return GetOrCreateIngredient(_booted(self._ingredient_repository))

    @cached_property
    def refresh_ingredient_catalog(self) -> RefreshIngredientCatalog:
        return RefreshIngredientCatalog(
            self._ingredient_source, _booted(self._ingredient_repository), self._logging
        )

    @cached_property
    def actuator(self) -> Actuator:
        return Actuator(
            name=APPLICATION_NAME,
            version=APPLICATION_VERSION,
            environment=APPLICATION_DEPLOYMENT_ENVIRONMENT,
            authors=APPLICATION_AUTHORS_EMAIL,
            is_ready=lambda: self._ready,
        )

    async def boot(self) -> None:
        _ = self._telemetry_provider
        self._ingredient_repository = await self._sql_ingredient_repository()
        self._recipe_repository = await self._mongo_recipe_repository()
        await self._start_factories()
        self._ready = True
        self.logging.info("Kitchen Atelier container booted")

    async def stop(self) -> None:
        self._ready = False
        await self._stop_factories()
        await self._shutdown_telemetry()
        self.logging.info("Kitchen Atelier container shut down")


def _booted[T](value: T | None) -> T:
    if value is None:
        raise RuntimeError(NOT_BOOTED)
    return value
