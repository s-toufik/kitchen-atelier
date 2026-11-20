import pytest

from kitchen_atelier.application.use_case.create_recipe import CreateRecipe
from kitchen_atelier.application.use_case.delete_recipe import DeleteRecipe
from kitchen_atelier.application.use_case.save_recipe_version import SaveRecipeVersion
from kitchen_atelier.domain.recipe.exception.recipe_not_found import RecipeNotFound
from kitchen_atelier.domain.recipe.ingredient_line import IngredientLine
from kitchen_atelier.domain.recipe.recipe_draft import RecipeDraft, Step
from kitchen_atelier.domain.recipe.unit import Unit
from tests.support.fakes import FakeRecipeRepository


def _draft() -> RecipeDraft:
    return RecipeDraft(
        title="Tarte au citron",
        subtitle="",
        course="Pastry",
        portions=8,
        prep_time_minutes=25,
        cook_time_minutes=30,
        ingredients=(
            IngredientLine(
                name="Citron",
                quantity=4,
                unit=Unit.PIECE,
                kcal_per_100g=29,
                protein_per_100g=1.1,
                carb_per_100g=9.3,
                fat_per_100g=0.3,
            ),
        ),
        steps=(Step(text="Cuire la pâte à blanc, verser la crème au citron, lisser."),),
    )


async def test_removes_the_recipe_and_every_version() -> None:
    repository = FakeRecipeRepository()
    recipe = await CreateRecipe(repository).handle(_draft())
    await SaveRecipeVersion(repository).handle(recipe.id, 1, _draft())

    await DeleteRecipe(repository).handle(recipe.id)

    assert await repository.get(recipe.id) is None
    assert await repository.list_versions(recipe.id) == []


async def test_raises_when_the_recipe_does_not_exist() -> None:
    with pytest.raises(RecipeNotFound):
        await DeleteRecipe(FakeRecipeRepository()).handle("missing")
