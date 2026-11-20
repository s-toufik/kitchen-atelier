from typing import Protocol, runtime_checkable


@runtime_checkable
class DeleteRecipePort(Protocol):
    async def handle(self, recipe_id: str) -> None: ...
