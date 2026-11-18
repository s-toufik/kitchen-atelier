from typing import Protocol, runtime_checkable

from kitchen_atelier.domain.recipe.recipe import Recipe
from kitchen_atelier.domain.recipe.recipe_version import RecipeVersion


@runtime_checkable
class RecipeRepository(Protocol):
    async def get(self, recipe_id: str) -> Recipe | None: ...

    async def list_recipes(self) -> list[Recipe]: ...

    async def get_version(self, recipe_id: str, version_number: int) -> RecipeVersion | None: ...

    async def list_versions(self, recipe_id: str) -> list[RecipeVersion]: ...

    async def save(self, recipe: Recipe, version: RecipeVersion) -> None:
        """Persist the new version, then advance the recipe header to point at it.

        MongoDB runs here as a single standalone instance, without multi-document
        transactions, so this is not atomic: a failure between the two writes leaves the
        version saved but the header not yet advanced. Both writes are idempotent upserts
        keyed on identity (recipe id; recipe id + version number), so retrying this call
        with the same arguments after a partial failure is always safe.
        """
        ...
