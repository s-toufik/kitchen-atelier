from pydantic import BaseModel

from kitchen_atelier.domain.recipe.nutrition import NutritionTotals


class MacroSplitSchema(BaseModel):
    protein_pct: float
    carb_pct: float
    fat_pct: float


class NutritionSchema(BaseModel):
    weight_grams: float
    kcal: float
    protein_g: float
    carb_g: float
    fat_g: float
    caloric_density_per_100g: float
    macro_split: MacroSplitSchema

    @classmethod
    def from_domain(cls, totals: NutritionTotals) -> NutritionSchema:
        split = totals.macro_split
        return cls(
            weight_grams=totals.weight_grams,
            kcal=totals.kcal,
            protein_g=totals.protein_g,
            carb_g=totals.carb_g,
            fat_g=totals.fat_g,
            caloric_density_per_100g=totals.caloric_density_per_100g,
            macro_split=MacroSplitSchema(
                protein_pct=split.protein_pct, carb_pct=split.carb_pct, fat_pct=split.fat_pct
            ),
        )
