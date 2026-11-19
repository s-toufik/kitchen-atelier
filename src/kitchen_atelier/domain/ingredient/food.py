from dataclasses import dataclass
from datetime import datetime

from kitchen_atelier.domain.ingredient.food_classification import FoodClassification
from kitchen_atelier.domain.ingredient.food_identity import FoodIdentity
from kitchen_atelier.domain.ingredient.nutritional_composition import NutritionalComposition


@dataclass(frozen=True, slots=True)
class Food:
    identity: FoodIdentity
    classification: FoodClassification
    nutrition: NutritionalComposition
    source: str
    source_version: str
    updated_at: datetime
