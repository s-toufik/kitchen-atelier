from kitchen_atelier.domain.recipe.ingredient_line import IngredientLine
from kitchen_atelier.domain.recipe.nutrition import totals_of
from kitchen_atelier.domain.recipe.unit import Unit


def _line(**overrides: object) -> IngredientLine:
    defaults: dict[str, object] = {
        "name": "Poulet",
        "quantity": 100,
        "unit": Unit.GRAM,
        "kcal_per_100g": 0,
        "protein_per_100g": 0,
        "carb_per_100g": 0,
        "fat_per_100g": 0,
    }
    return IngredientLine(**(defaults | overrides))


def test_totals_sum_every_line() -> None:
    lines = [
        _line(quantity=200, kcal_per_100g=100, protein_per_100g=10),
        _line(quantity=100, kcal_per_100g=50, protein_per_100g=5),
    ]
    totals = totals_of(lines)
    assert totals.weight_grams == 300
    assert totals.kcal == 250
    assert totals.protein_g == 25


def test_per_portion_divides_every_field() -> None:
    totals = totals_of([_line(quantity=400, kcal_per_100g=100)])
    per_portion = totals.per_portion(4)
    assert per_portion.weight_grams == 100
    assert per_portion.kcal == 100


def test_caloric_density_is_zero_with_no_weight() -> None:
    assert totals_of([]).caloric_density_per_100g == 0


def test_macro_split_sums_to_one_hundred() -> None:
    totals = totals_of(
        [_line(quantity=100, protein_per_100g=20, carb_per_100g=20, fat_per_100g=10)]
    )
    split = totals.macro_split
    assert round(split.protein_pct + split.carb_pct + split.fat_pct) == 100


def test_macro_split_is_zero_with_no_macros() -> None:
    split = totals_of([_line(quantity=100)]).macro_split
    assert (split.protein_pct, split.carb_pct, split.fat_pct) == (0.0, 0.0, 0.0)
