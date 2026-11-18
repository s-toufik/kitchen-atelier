from dataclasses import dataclass, replace
from datetime import datetime

from kitchen_atelier.domain.recipe.recipe_version import RecipeVersion


@dataclass(frozen=True, slots=True)
class Recipe:
    id: str
    title: str
    course: str
    current_version_number: int
    created_at: datetime
    updated_at: datetime

    def __post_init__(self) -> None:
        if not self.id.strip():
            raise ValueError("a recipe needs an id")
        if self.current_version_number < 1:
            raise ValueError("current_version_number must be 1 or more")

    @classmethod
    def start(cls, recipe_id: str, first_version: RecipeVersion, created_at: datetime) -> Recipe:
        if first_version.recipe_id != recipe_id:
            raise ValueError("version does not belong to this recipe")
        if first_version.version_number != 1:
            raise ValueError("the first version of a recipe must be version 1")
        return cls(
            id=recipe_id,
            title=first_version.title,
            course=first_version.draft.course,
            current_version_number=1,
            created_at=created_at,
            updated_at=created_at,
        )

    def with_new_version(self, version: RecipeVersion, saved_at: datetime) -> Recipe:
        if version.recipe_id != self.id:
            raise ValueError("version does not belong to this recipe")
        if version.version_number != self.current_version_number + 1:
            raise ValueError(
                f"expected version {self.current_version_number + 1}, got {version.version_number}"
            )
        return replace(
            self,
            title=version.title,
            course=version.draft.course,
            current_version_number=version.version_number,
            updated_at=saved_at,
        )
