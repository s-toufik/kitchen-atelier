from typing import Protocol, runtime_checkable

from kitchen_atelier.domain.recipe.recipe import Recipe


@runtime_checkable
class ListRecipesPort(Protocol):
    async def handle(self) -> list[Recipe]: ...
