from dataclasses import dataclass

from kitchen_atelier.domain.ingredient.nutrient import Nutrient


@dataclass(frozen=True, slots=True)
class FattyAcids:
    saturated_g: Nutrient = None
    monounsaturated_g: Nutrient = None
    polyunsaturated_g: Nutrient = None
    butyric_acid_4_0_g: Nutrient = None
    caproic_acid_6_0_g: Nutrient = None
    caprylic_acid_8_0_g: Nutrient = None
    capric_acid_10_0_g: Nutrient = None
    lauric_acid_12_0_g: Nutrient = None
    myristic_acid_14_0_g: Nutrient = None
    palmitic_acid_16_0_g: Nutrient = None
    stearic_acid_18_0_g: Nutrient = None
    oleic_acid_18_1_g: Nutrient = None
    linoleic_acid_18_2_g: Nutrient = None
    alpha_linolenic_acid_18_3_g: Nutrient = None
    arachidonic_acid_20_4_g: Nutrient = None
    epa_20_5_g: Nutrient = None
    dha_22_6_g: Nutrient = None
