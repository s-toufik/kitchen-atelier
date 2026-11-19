from dataclasses import dataclass

from kitchen_atelier.domain.ingredient.nutrient import Nutrient


@dataclass(frozen=True, slots=True)
class Macronutrients:
    water_g: Nutrient = None
    protein_jones_g: Nutrient = None
    protein_6_25_g: Nutrient = None
    carbohydrates_g: Nutrient = None
    fat_g: Nutrient = None
    dietary_fiber_g: Nutrient = None
    total_polyols_g: Nutrient = None
    ash_g: Nutrient = None
    alcohol_g: Nutrient = None
    organic_acids_g: Nutrient = None
