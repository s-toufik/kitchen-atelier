from pydantic import BaseModel

from kitchen_atelier.domain.ingredient.ingredient import Ingredient


class IngredientSchema(BaseModel):
    ciqual_code: str
    name_fr: str
    kcal_per_100g: float
    protein_per_100g: float
    carb_per_100g: float
    fat_per_100g: float

    @classmethod
    def from_domain(cls, ingredient: Ingredient) -> IngredientSchema:
        return cls(
            ciqual_code=ingredient.ciqual_code,
            name_fr=ingredient.name_fr,
            kcal_per_100g=ingredient.kcal_per_100g,
            protein_per_100g=ingredient.protein_per_100g,
            carb_per_100g=ingredient.carb_per_100g,
            fat_per_100g=ingredient.fat_per_100g,
        )


class IngredientListSchema(BaseModel):
    ingredients: list[IngredientSchema]

    @classmethod
    def from_domain(cls, ingredients: list[Ingredient]) -> IngredientListSchema:
        return cls(ingredients=[IngredientSchema.from_domain(item) for item in ingredients])
