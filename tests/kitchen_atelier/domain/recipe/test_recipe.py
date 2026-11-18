from datetime import UTC, datetime

import pytest

from kitchen_atelier.domain.recipe.ingredient_line import IngredientLine
from kitchen_atelier.domain.recipe.recipe import Recipe
from kitchen_atelier.domain.recipe.recipe_draft import RecipeDraft, Step
from kitchen_atelier.domain.recipe.recipe_version import RecipeVersion
from kitchen_atelier.domain.recipe.unit import Unit


def _draft(title: str = "Ratatouille") -> RecipeDraft:
    return RecipeDraft(
        title=title,
        subtitle="",
        course="Main",
        portions=4,
        prep_time_minutes=20,
        cook_time_minutes=40,
        ingredients=(
            IngredientLine(
                name="Courgette",
                quantity=300,
                unit=Unit.GRAM,
                kcal_per_100g=17,
                protein_per_100g=1.2,
                carb_per_100g=3.1,
                fat_per_100g=0.3,
            ),
        ),
        steps=(Step(text="Couper les légumes en dés et les faire revenir."),),
    )


def test_start_creates_version_one() -> None:
    now = datetime.now(UTC)
    version = RecipeVersion(recipe_id="r1", version_number=1, saved_at=now, draft=_draft())
    recipe = Recipe.start("r1", version, now)
    assert recipe.current_version_number == 1
    assert recipe.title == "Ratatouille"


def test_start_rejects_a_version_that_is_not_number_one() -> None:
    now = datetime.now(UTC)
    version = RecipeVersion(recipe_id="r1", version_number=2, saved_at=now, draft=_draft())
    with pytest.raises(ValueError, match="version 1"):
        Recipe.start("r1", version, now)


def test_with_new_version_advances_current_version_and_title() -> None:
    now = datetime.now(UTC)
    first = RecipeVersion(recipe_id="r1", version_number=1, saved_at=now, draft=_draft())
    recipe = Recipe.start("r1", first, now)

    later = datetime.now(UTC)
    second = RecipeVersion(
        recipe_id="r1", version_number=2, saved_at=later, draft=_draft("Ratatouille (v2)")
    )
    updated = recipe.with_new_version(second, later)

    assert updated.current_version_number == 2
    assert updated.title == "Ratatouille (v2)"
    assert updated.updated_at == later


def test_with_new_version_rejects_skipping_a_version_number() -> None:
    now = datetime.now(UTC)
    first = RecipeVersion(recipe_id="r1", version_number=1, saved_at=now, draft=_draft())
    recipe = Recipe.start("r1", first, now)

    skipped = RecipeVersion(recipe_id="r1", version_number=3, saved_at=now, draft=_draft())
    with pytest.raises(ValueError, match="expected version 2"):
        recipe.with_new_version(skipped, now)
