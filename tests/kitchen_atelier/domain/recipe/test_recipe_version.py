from datetime import UTC, datetime

import pytest

from kitchen_atelier.domain.recipe.ingredient_line import IngredientLine
from kitchen_atelier.domain.recipe.recipe_draft import RecipeDraft, Step
from kitchen_atelier.domain.recipe.recipe_version import RecipeVersion
from kitchen_atelier.domain.recipe.unit import Unit


def _draft() -> RecipeDraft:
    return RecipeDraft(
        title="Soupe au pistou",
        subtitle="",
        course="Starter",
        portions=4,
        prep_time_minutes=20,
        cook_time_minutes=30,
        ingredients=(
            IngredientLine(
                name="Haricots blancs",
                quantity=200,
                unit=Unit.GRAM,
                kcal_per_100g=127,
                protein_per_100g=8.3,
                carb_per_100g=21.0,
                fat_per_100g=0.5,
            ),
        ),
        steps=(Step(text="Faire mijoter les légumes 30 minutes."),),
    )


def _version(**overrides: object) -> RecipeVersion:
    defaults: dict[str, object] = {
        "recipe_id": "abc123",
        "version_number": 1,
        "saved_at": datetime.now(UTC),
        "draft": _draft(),
    }
    return RecipeVersion(**(defaults | overrides))


def test_rejects_a_blank_recipe_id() -> None:
    with pytest.raises(ValueError, match="recipe_id"):
        _version(recipe_id=" ")


def test_rejects_version_number_below_one() -> None:
    with pytest.raises(ValueError, match="version_number"):
        _version(version_number=0)


def test_title_delegates_to_the_draft() -> None:
    assert _version().title == "Soupe au pistou"


def test_next_draft_is_an_independent_copy() -> None:
    version = _version()
    draft = version.next_draft()
    assert draft == version.draft
    assert draft is not version.draft
