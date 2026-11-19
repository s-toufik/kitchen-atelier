from dataclasses import dataclass

from kitchen_atelier.domain.ingredient.nutrient import Nutrient


@dataclass(frozen=True, slots=True)
class Energy:
    regulation_1169_kj: Nutrient = None
    regulation_1169_kcal: Nutrient = None
    jones_with_fiber_kj: Nutrient = None
    jones_with_fiber_kcal: Nutrient = None
