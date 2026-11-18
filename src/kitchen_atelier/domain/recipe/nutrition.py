from collections.abc import Iterable
from dataclasses import dataclass

from kitchen_atelier.domain.recipe.ingredient_line import IngredientLine

_PROTEIN_KCAL_PER_GRAM: float = 4.0
_CARB_KCAL_PER_GRAM: float = 4.0
_FAT_KCAL_PER_GRAM: float = 9.0


@dataclass(frozen=True, slots=True)
class MacroSplit:

    protein_pct: float
    carb_pct: float
    fat_pct: float


@dataclass(frozen=True, slots=True)
class NutritionTotals:
    weight_grams: float
    kcal: float
    protein_g: float
    carb_g: float
    fat_g: float

    def per_portion(self, portions: int) -> NutritionTotals:
        if portions < 1:
            raise ValueError("portions must be 1 or more")
        return NutritionTotals(
            weight_grams=self.weight_grams / portions,
            kcal=self.kcal / portions,
            protein_g=self.protein_g / portions,
            carb_g=self.carb_g / portions,
            fat_g=self.fat_g / portions,
        )

    @property
    def caloric_density_per_100g(self) -> float:
        return (self.kcal / self.weight_grams * 100) if self.weight_grams > 0 else 0.0

    @property
    def macro_split(self) -> MacroSplit:
        macro_kcal = (
            self.protein_g * _PROTEIN_KCAL_PER_GRAM
            + self.carb_g * _CARB_KCAL_PER_GRAM
            + self.fat_g * _FAT_KCAL_PER_GRAM
        )
        if macro_kcal <= 0:
            return MacroSplit(0.0, 0.0, 0.0)
        protein_pct = self.protein_g * _PROTEIN_KCAL_PER_GRAM / macro_kcal * 100
        carb_pct = self.carb_g * _CARB_KCAL_PER_GRAM / macro_kcal * 100
        fat_pct = max(0.0, 100.0 - protein_pct - carb_pct)
        return MacroSplit(protein_pct, carb_pct, fat_pct)


def totals_of(lines: Iterable[IngredientLine]) -> NutritionTotals:
    weight = kcal = protein = carb = fat = 0.0
    for line in lines:
        weight += line.grams
        kcal += line.kcal()
        protein += line.protein()
        carb += line.carb()
        fat += line.fat()
    return NutritionTotals(weight, kcal, protein, carb, fat)
