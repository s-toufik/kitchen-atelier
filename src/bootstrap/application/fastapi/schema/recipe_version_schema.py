from datetime import datetime

from pydantic import BaseModel

from bootstrap.application.fastapi.schema.nutrition_schema import NutritionSchema
from bootstrap.application.fastapi.schema.recipe_draft_schema import RecipeDraftSchema
from kitchen_atelier.domain.recipe.recipe_version import RecipeVersion


class RecipeVersionSchema(BaseModel):
    recipe_id: str
    version_number: int
    saved_at: datetime
    draft: RecipeDraftSchema
    nutrition_per_portion: NutritionSchema
    nutrition_total: NutritionSchema

    @classmethod
    def from_domain(cls, version: RecipeVersion) -> RecipeVersionSchema:
        return cls(
            recipe_id=version.recipe_id,
            version_number=version.version_number,
            saved_at=version.saved_at,
            draft=RecipeDraftSchema.from_domain(version.draft),
            nutrition_per_portion=NutritionSchema.from_domain(version.nutrition_per_portion()),
            nutrition_total=NutritionSchema.from_domain(version.nutrition()),
        )


class RecipeVersionListSchema(BaseModel):
    versions: list[RecipeVersionSchema]

    @classmethod
    def from_domain(cls, versions: list[RecipeVersion]) -> RecipeVersionListSchema:
        return cls(versions=[RecipeVersionSchema.from_domain(version) for version in versions])
