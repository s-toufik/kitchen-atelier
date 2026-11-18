from pydantic import BaseModel, Field


class CreateIngredientRequestSchema(BaseModel):
    name_fr: str = Field(min_length=1, max_length=300)
    kcal_per_100g: float = 0
    protein_per_100g: float = 0
    carb_per_100g: float = 0
    fat_per_100g: float = 0
