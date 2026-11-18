from datetime import datetime

from pydantic import BaseModel

from kitchen_atelier.domain.recipe.recipe import Recipe


class RecipeSchema(BaseModel):
    id: str
    title: str
    course: str
    current_version_number: int
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_domain(cls, recipe: Recipe) -> RecipeSchema:
        return cls(
            id=recipe.id,
            title=recipe.title,
            course=recipe.course,
            current_version_number=recipe.current_version_number,
            created_at=recipe.created_at,
            updated_at=recipe.updated_at,
        )


class RecipeListSchema(BaseModel):
    recipes: list[RecipeSchema]

    @classmethod
    def from_domain(cls, recipes: list[Recipe]) -> RecipeListSchema:
        return cls(recipes=[RecipeSchema.from_domain(recipe) for recipe in recipes])
