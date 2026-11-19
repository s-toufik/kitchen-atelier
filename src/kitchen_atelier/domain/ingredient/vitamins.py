from dataclasses import dataclass

from kitchen_atelier.domain.ingredient.nutrient import Nutrient


@dataclass(frozen=True, slots=True)
class Vitamins:
    retinol_ug: Nutrient = None
    beta_carotene_ug: Nutrient = None
    vitamin_d_ug: Nutrient = None
    vitamin_e_mg: Nutrient = None
    vitamin_k1_ug: Nutrient = None
    vitamin_k2_ug: Nutrient = None
    vitamin_c_mg: Nutrient = None
    vitamin_b1_mg: Nutrient = None
    vitamin_b2_mg: Nutrient = None
    vitamin_b3_mg: Nutrient = None
    vitamin_b5_mg: Nutrient = None
    vitamin_b6_mg: Nutrient = None
    vitamin_b9_ug: Nutrient = None
    vitamin_b12_ug: Nutrient = None
