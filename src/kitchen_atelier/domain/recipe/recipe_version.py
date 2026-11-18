from dataclasses import dataclass, replace
from datetime import datetime

from kitchen_atelier.domain.recipe.ingredient_line import IngredientLine
from kitchen_atelier.domain.recipe.nutrition import NutritionTotals
from kitchen_atelier.domain.recipe.recipe_draft import RecipeDraft, Sensory, Step

__all__ = ["RecipeVersion", "RecipeDraft", "Sensory", "Step"]


@dataclass(frozen=True, slots=True)
class RecipeVersion:
    """An immutable snapshot of a recipe's full card at the moment it was saved.

    Versions are never edited in place: saving always appends the next version number,
    and switching the version selector just renders an already-saved snapshot.
    """

    recipe_id: str
    version_number: int
    saved_at: datetime
    draft: RecipeDraft

    def __post_init__(self) -> None:
        if not self.recipe_id.strip():
            raise ValueError("a recipe version needs a recipe_id")
        if self.version_number < 1:
            raise ValueError("version_number must be 1 or more")

    @property
    def title(self) -> str:
        return self.draft.title

    def nutrition(self) -> NutritionTotals:
        return self.draft.nutrition()

    def nutrition_per_portion(self) -> NutritionTotals:
        return self.draft.nutrition_per_portion()

    def scaled_ingredients(self, portions: int) -> tuple[IngredientLine, ...]:
        return self.draft.scaled_ingredients(portions)

    def next_draft(self) -> RecipeDraft:
        """A starting point for editing: the same content, pre-filled for a new save."""
        return replace(self.draft)
