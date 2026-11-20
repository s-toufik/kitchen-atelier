import asyncio

from pymongo import MongoClient

from kitchen_atelier.adapter.outbound.mongo.recipe_mapper import (
    recipe_from_document,
    recipe_to_document,
    version_from_document,
    version_to_document,
)
from kitchen_atelier.domain.recipe.recipe import Recipe
from kitchen_atelier.domain.recipe.recipe_version import RecipeVersion


class MongoRecipeRepository:
    def __init__(self, client: MongoClient, database: str, recipes: str, versions: str) -> None:
        db = client[database]
        self._recipes = db[recipes]
        self._versions = db[versions]

    async def ensure_indexes(self) -> None:
        await asyncio.to_thread(
            self._versions.create_index,
            [("recipe_id", 1), ("version_number", 1)],
            unique=True,
            name="recipe_id_version_number",
        )

    async def get(self, recipe_id: str) -> Recipe | None:
        document = await asyncio.to_thread(self._recipes.find_one, {"_id": recipe_id})
        return recipe_from_document(document) if document is not None else None

    async def list_recipes(self) -> list[Recipe]:
        documents = await asyncio.to_thread(lambda: list(self._recipes.find()))
        return [recipe_from_document(document) for document in documents]

    async def get_version(self, recipe_id: str, version_number: int) -> RecipeVersion | None:
        document = await asyncio.to_thread(
            self._versions.find_one,
            {"recipe_id": recipe_id, "version_number": version_number},
        )
        return version_from_document(document) if document is not None else None

    async def list_versions(self, recipe_id: str) -> list[RecipeVersion]:
        documents = await asyncio.to_thread(
            lambda: list(self._versions.find({"recipe_id": recipe_id}))
        )
        return [version_from_document(document) for document in documents]

    async def save(self, recipe: Recipe, version: RecipeVersion) -> None:
        await asyncio.to_thread(
            self._versions.replace_one,
            {"recipe_id": version.recipe_id, "version_number": version.version_number},
            version_to_document(version),
            upsert=True,
        )
        await asyncio.to_thread(
            self._recipes.replace_one,
            {"_id": recipe.id},
            recipe_to_document(recipe),
            upsert=True,
        )

    async def delete(self, recipe_id: str) -> None:
        await asyncio.to_thread(self._versions.delete_many, {"recipe_id": recipe_id})
        await asyncio.to_thread(self._recipes.delete_one, {"_id": recipe_id})
