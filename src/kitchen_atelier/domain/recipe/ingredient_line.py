from dataclasses import dataclass, replace

from kitchen_atelier.domain.recipe.unit import Unit, to_grams

_NON_NEGATIVE_FIELDS: tuple[str, ...] = (
    "kcal_per_100g",
    "protein_per_100g",
    "carb_per_100g",
    "fat_per_100g",
)


@dataclass(frozen=True, slots=True)
class IngredientLine:

    name: str
    quantity: float
    unit: Unit
    kcal_per_100g: float
    protein_per_100g: float
    carb_per_100g: float
    fat_per_100g: float
    ingredient_ref_id: str | None = None

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("an ingredient line needs a name")
        if self.quantity < 0:
            raise ValueError(f"ingredient line {self.name!r}: quantity must be 0 or more")
        for field_name in _NON_NEGATIVE_FIELDS:
            if getattr(self, field_name) < 0:
                raise ValueError(f"ingredient line {self.name!r}: {field_name} must be 0 or more")

    @property
    def grams(self) -> float:
        return to_grams(self.quantity, self.unit)

    def scaled(self, factor: float) -> IngredientLine:
        if factor <= 0:
            raise ValueError("scale factor must be greater than 0")
        return replace(self, quantity=round(self.quantity * factor, 2))

    def kcal(self) -> float:
        return self.grams / 100 * self.kcal_per_100g

    def protein(self) -> float:
        return self.grams / 100 * self.protein_per_100g

    def carb(self) -> float:
        return self.grams / 100 * self.carb_per_100g

    def fat(self) -> float:
        return self.grams / 100 * self.fat_per_100g
