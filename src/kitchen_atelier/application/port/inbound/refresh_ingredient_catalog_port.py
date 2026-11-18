from typing import Protocol, runtime_checkable


@runtime_checkable
class RefreshIngredientCatalogPort(Protocol):
    async def handle(self) -> int: ...
