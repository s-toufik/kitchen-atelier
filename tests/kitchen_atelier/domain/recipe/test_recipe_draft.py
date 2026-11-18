import pytest

from kitchen_atelier.domain.recipe.ingredient_line import IngredientLine
from kitchen_atelier.domain.recipe.recipe_draft import RecipeDraft, Step
from kitchen_atelier.domain.recipe.unit import Unit


def _ingredient(quantity: float = 100) -> IngredientLine:
    return IngredientLine(
        name="Pomme de terre",
        quantity=quantity,
        unit=Unit.GRAM,
        kcal_per_100g=77,
        protein_per_100g=2.0,
        carb_per_100g=17.5,
        fat_per_100g=0.1,
    )


def _draft(**overrides: object) -> RecipeDraft:
    defaults: dict[str, object] = {
        "title": "Gratin dauphinois",
        "subtitle": "",
        "course": "Main",
        "portions": 4,
        "prep_time_minutes": 15,
        "cook_time_minutes": 45,
        "ingredients": (_ingredient(),),
        "steps": (Step(text="Peler et émincer les pommes de terre."),),
    }
    return RecipeDraft(**(defaults | overrides))


def test_rejects_a_blank_title() -> None:
    with pytest.raises(ValueError, match="title"):
        _draft(title=" ")


def test_rejects_zero_portions() -> None:
    with pytest.raises(ValueError, match="portions"):
        _draft(portions=0)


def test_rejects_an_empty_ingredient_list() -> None:
    with pytest.raises(ValueError, match="ingredient"):
        _draft(ingredients=())


def test_rejects_an_empty_step_list() -> None:
    with pytest.raises(ValueError, match="step"):
        _draft(steps=())


def test_nutrition_per_portion_divides_by_portions() -> None:
    draft = _draft(portions=2, ingredients=(_ingredient(quantity=400),))
    assert draft.nutrition_per_portion().weight_grams == 200


def test_scaled_ingredients_keeps_the_ratio_to_the_original_portions() -> None:
    draft = _draft(portions=4, ingredients=(_ingredient(quantity=100),))
    scaled = draft.scaled_ingredients(8)
    assert scaled[0].quantity == 200
