from functools import cached_property

from pycraftcore.application_configuration.model.connector import ApiConnector
from pycraftcore.application_configuration.model.operation import DatabaseOperation
from pycraftcore.repository.adapter import (
    MongoRepositoryFactory,
    MongoSettingsMapper,
    PostgresEngineBuilder,
    PostgresSettingsMapper,
    SqlAlchemyRepositoryFactory,
)
from pycraftcore.repository.port import AsyncRepository
from pymongo import MongoClient

from bootstrap.di.base_di import BaseDI
from kitchen_atelier.adapter.outbound.ingestion.http_ingredient_source import HttpIngredientSource
from kitchen_atelier.adapter.outbound.mongo.recipe_repository import MongoRecipeRepository
from kitchen_atelier.adapter.outbound.sql.ingredient_repository import SqlIngredientRepository
from kitchen_atelier.application.port.outbound.ingredient_repository_port import (
    IngredientRepository,
)

__all__ = ["KitchenDI"]

INGREDIENTS_OPERATION: str = "ingredients"
RECIPES_OPERATION: str = "recipes"
CIQUAL_CONNECTOR: str = "ciqual"

RECIPES_COLLECTION_ROLE: str = "recipes"
VERSIONS_COLLECTION_ROLE: str = "versions"


class KitchenDI(BaseDI):
    async def _sql_ingredient_repository(self) -> IngredientRepository:
        operation: DatabaseOperation = self._configuration.operation.database(
            INGREDIENTS_OPERATION
        )
        factory = SqlAlchemyRepositoryFactory(
            PostgresEngineBuilder(PostgresSettingsMapper(operation)())
        )
        self._register_repository(factory)
        repository: AsyncRepository = await factory.connect()
        return SqlIngredientRepository(repository)

    async def _mongo_recipe_repository(self) -> MongoRecipeRepository:
        operation: DatabaseOperation = self._configuration.operation.database(RECIPES_OPERATION)
        factory = MongoRepositoryFactory(MongoSettingsMapper(operation)())
        self._register_repository(factory)
        client: MongoClient = await factory.connection()
        repository = MongoRecipeRepository(
            client,
            operation.database,
            operation.collection(RECIPES_COLLECTION_ROLE),
            operation.collection(VERSIONS_COLLECTION_ROLE),
        )
        await repository.ensure_indexes()
        return repository

    @cached_property
    def _ingredient_source(self) -> HttpIngredientSource:
        connector: ApiConnector = self._configuration.connector.api(CIQUAL_CONNECTOR)
        return HttpIngredientSource(connector, self._logging)
