from pydantic import BaseModel

from kitchen_atelier.domain.ingredient.food import Food
from kitchen_atelier.domain.ingredient.food_classification import FoodClassification
from kitchen_atelier.domain.ingredient.nutritional_composition import NutritionalComposition


class IngredientSchema(BaseModel):
    ciqual_code: str
    name_fr: str
    scientific_name: str | None
    classification: FoodClassification
    kcal_per_100g: float
    protein_per_100g: float
    carb_per_100g: float
    fat_per_100g: float
    source: str
    source_version: str
    nutrition: NutritionalComposition

    @classmethod
    def from_domain(cls, food: Food) -> IngredientSchema:
        return cls(
            ciqual_code=food.identity.ciqual_code,
            name_fr=food.identity.name,
            scientific_name=food.identity.scientific_name,
            classification=food.classification,
            kcal_per_100g=float(food.nutrition.energy.regulation_1169_kcal or 0),
            protein_per_100g=float(food.nutrition.macronutrients.protein_jones_g or 0),
            carb_per_100g=float(food.nutrition.macronutrients.carbohydrates_g or 0),
            fat_per_100g=float(food.nutrition.macronutrients.fat_g or 0),
            source=food.source,
            source_version=food.source_version,
            nutrition=food.nutrition,
        )


class IngredientListSchema(BaseModel):
    ingredients: list[IngredientSchema]

    @classmethod
    def from_domain(cls, foods: list[Food]) -> IngredientListSchema:
        return cls(ingredients=[IngredientSchema.from_domain(food) for food in foods])
