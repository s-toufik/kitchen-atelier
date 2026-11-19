from dataclasses import dataclass

from kitchen_atelier.domain.ingredient.energy import Energy
from kitchen_atelier.domain.ingredient.fatty_acids import FattyAcids
from kitchen_atelier.domain.ingredient.macronutrients import Macronutrients
from kitchen_atelier.domain.ingredient.minerals import Minerals
from kitchen_atelier.domain.ingredient.sugars import Sugars
from kitchen_atelier.domain.ingredient.vitamins import Vitamins


@dataclass(frozen=True, slots=True)
class NutritionalComposition:
    energy: Energy
    macronutrients: Macronutrients
    sugars: Sugars
    fatty_acids: FattyAcids
    minerals: Minerals
    vitamins: Vitamins
