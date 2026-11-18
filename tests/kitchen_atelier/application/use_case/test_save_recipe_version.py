from dataclasses import replace

import pytest

from kitchen_atelier.application.use_case.create_recipe import CreateRecipe
from kitchen_atelier.application.use_case.save_recipe_version import SaveRecipeVersion
from kitchen_atelier.domain.recipe.exception.recipe_not_found import RecipeNotFound
from kitchen_atelier.domain.recipe.exception.stale_version import StaleVersion
from kitchen_atelier.domain.recipe.ingredient_line import IngredientLine
from kitchen_atelier.domain.recipe.recipe_draft import RecipeDraft, Step
from kitchen_atelier.domain.recipe.unit import Unit
from tests.support.fakes import FakeRecipeRepository


def _draft() -> RecipeDraft:
    return RecipeDraft(
        title="Quiche lorraine",
        subtitle="",
        course="Main",
        portions=6,
        prep_time_minutes=20,
        cook_time_minutes=35,
        ingredients=(
            IngredientLine(
                name="Lardons",
                quantity=150,
                unit=Unit.GRAM,
                kcal_per_100g=280,
                protein_per_100g=20.0,
                carb_per_100g=0.0,
                fat_per_100g=22.0,
            ),
        ),
        steps=(Step(text="Mélanger les oeufs et la crème, verser sur la pâte."),),
    )


async def test_appends_the_next_version() -> None:
    repository = FakeRecipeRepository()
    recipe = await CreateRecipe(repository).handle(_draft())

    revised = replace(_draft(), title="Quiche lorraine (moins de lardons)")
    version = await SaveRecipeVersion(repository).handle(recipe.id, 1, revised)

    assert version.version_number == 2
    updated_recipe = await repository.get(recipe.id)
    assert updated_recipe is not None
    assert updated_recipe.current_version_number == 2
    assert updated_recipe.title == "Quiche lorraine (moins de lardons)"


async def test_raises_when_the_recipe_does_not_exist() -> None:
    with pytest.raises(RecipeNotFound):
        await SaveRecipeVersion(FakeRecipeRepository()).handle("missing", 1, _draft())


async def test_raises_when_the_draft_was_based_on_a_stale_version() -> None:
    repository = FakeRecipeRepository()
    recipe = await CreateRecipe(repository).handle(_draft())
    await SaveRecipeVersion(repository).handle(recipe.id, 1, _draft())

    with pytest.raises(StaleVersion):
        await SaveRecipeVersion(repository).handle(recipe.id, 1, _draft())
