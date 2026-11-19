from dataclasses import dataclass

from kitchen_atelier.domain.ingredient.nutrient import Nutrient


@dataclass(frozen=True, slots=True)
class Minerals:
    cholesterol_mg: Nutrient = None
    sodium_chloride_g: Nutrient = None
    calcium_mg: Nutrient = None
    chloride_mg: Nutrient = None
    copper_mg: Nutrient = None
    iron_mg: Nutrient = None
    iodine_ug: Nutrient = None
    magnesium_mg: Nutrient = None
    manganese_mg: Nutrient = None
    phosphorus_mg: Nutrient = None
    potassium_mg: Nutrient = None
    selenium_ug: Nutrient = None
    sodium_mg: Nutrient = None
    zinc_mg: Nutrient = None
