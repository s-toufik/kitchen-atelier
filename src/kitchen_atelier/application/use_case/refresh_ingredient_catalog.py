from pycraftcore.logger.port import Logger

from kitchen_atelier.application.port.outbound.ingredient_repository_port import (
    IngredientRepository,
)
from kitchen_atelier.application.port.outbound.ingredient_source_port import IngredientSource


class RefreshIngredientCatalog:
    """Re-fetches the source catalog (CIQUAL) and upserts it. Run by the scheduled job."""

    def __init__(
        self, source: IngredientSource, repository: IngredientRepository, logger: Logger
    ) -> None:
        self._source = source
        self._repository = repository
        self._logger = logger

    async def handle(self) -> int:
        ingredients = await self._source.fetch_all()
        if not ingredients:
            self._logger.warning("Ingredient source returned no rows; catalog left unchanged")
            return 0

        changed = await self._repository.upsert_many(ingredients)
        self._logger.info(
            f"Ingredient catalog refresh: {changed} changed out of {len(ingredients)} fetched"
        )
        return changed
