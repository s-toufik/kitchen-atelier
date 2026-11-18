from typing import Protocol, runtime_checkable


@runtime_checkable
class RefreshIngredientCatalogPort(Protocol):
    async def handle(self) -> int:
        """Re-fetch the source catalog and upsert it; returns how many rows changed."""
        ...
