from dataclasses import dataclass

from kitchen_atelier.domain.ingredient.nutrient import Nutrient


@dataclass(frozen=True, slots=True)
class Sugars:
    total_sugars_g: Nutrient = None
    fructose_g: Nutrient = None
    galactose_g: Nutrient = None
    glucose_g: Nutrient = None
    lactose_g: Nutrient = None
    maltose_g: Nutrient = None
    sucrose_g: Nutrient = None
    starch_g: Nutrient = None
