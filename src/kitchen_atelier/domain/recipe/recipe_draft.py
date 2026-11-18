from dataclasses import dataclass, field

from kitchen_atelier.domain.recipe.ingredient_line import IngredientLine
from kitchen_atelier.domain.recipe.nutrition import NutritionTotals, totals_of


@dataclass(frozen=True, slots=True)
class Sensory:
    seasoning: str = "Balanced"
    acidity: str = "Balanced"
    texture: str = "Spot-On"


@dataclass(frozen=True, slots=True)
class Step:
    text: str
    tags: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.text.strip():
            raise ValueError("a method step needs text")


@dataclass(frozen=True, slots=True)
class RecipeDraft:

    title: str
    subtitle: str
    course: str
    portions: int
    prep_time_minutes: int
    cook_time_minutes: int
    ingredients: tuple[IngredientLine, ...]
    steps: tuple[Step, ...]
    sensory: Sensory = field(default_factory=Sensory)
    notes: str = ""

    def __post_init__(self) -> None:
        if not self.title.strip():
            raise ValueError("a recipe draft needs a title")
        if self.portions < 1:
            raise ValueError("portions must be 1 or more")
        if self.prep_time_minutes < 0 or self.cook_time_minutes < 0:
            raise ValueError("prep/cook time must be 0 or more")
        if not self.ingredients:
            raise ValueError("a recipe draft needs at least one ingredient")
        if not self.steps:
            raise ValueError("a recipe draft needs at least one method step")

    def nutrition(self) -> NutritionTotals:
        return totals_of(self.ingredients)

    def nutrition_per_portion(self) -> NutritionTotals:
        return self.nutrition().per_portion(self.portions)

    def scaled_ingredients(self, portions: int) -> tuple[IngredientLine, ...]:
        if portions < 1:
            raise ValueError("portions must be 1 or more")
        factor = portions / self.portions
        return tuple(line.scaled(factor) for line in self.ingredients)
