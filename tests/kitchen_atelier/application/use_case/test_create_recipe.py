from kitchen_atelier.application.use_case.create_recipe import CreateRecipe
from kitchen_atelier.domain.recipe.ingredient_line import IngredientLine
from kitchen_atelier.domain.recipe.recipe_draft import RecipeDraft, Step
from kitchen_atelier.domain.recipe.unit import Unit
from tests.support.fakes import FakeRecipeRepository


def _draft() -> RecipeDraft:
    return RecipeDraft(
        title="Tarte aux pommes",
        subtitle="",
        course="Pastry",
        portions=6,
        prep_time_minutes=30,
        cook_time_minutes=40,
        ingredients=(
            IngredientLine(
                name="Pommes",
                quantity=600,
                unit=Unit.GRAM,
                kcal_per_100g=52,
                protein_per_100g=0.3,
                carb_per_100g=14.0,
                fat_per_100g=0.2,
            ),
        ),
        steps=(Step(text="Disposer les pommes sur la pâte et enfourner."),),
    )


async def test_creates_a_recipe_at_version_one() -> None:
    repository = FakeRecipeRepository()
    recipe = await CreateRecipe(repository).handle(_draft())

    assert recipe.current_version_number == 1
    assert recipe.title == "Tarte aux pommes"
    saved_version = await repository.get_version(recipe.id, 1)
    assert saved_version is not None
    assert saved_version.draft == _draft()
