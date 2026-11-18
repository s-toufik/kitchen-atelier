from pydantic import BaseModel, Field

from bootstrap.application.fastapi.schema.recipe_draft_schema import RecipeDraftSchema


class SaveRecipeVersionRequestSchema(BaseModel):
    based_on_version: int = Field(ge=1)
    draft: RecipeDraftSchema
