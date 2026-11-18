import pytest

from kitchen_atelier.domain.recipe.ingredient_line import IngredientLine
from kitchen_atelier.domain.recipe.unit import Unit


def _line(**overrides: object) -> IngredientLine:
    defaults: dict[str, object] = {
        "name": "Beurre doux",
        "quantity": 100,
        "unit": Unit.GRAM,
        "kcal_per_100g": 717,
        "protein_per_100g": 0.9,
        "carb_per_100g": 0.1,
        "fat_per_100g": 81.1,
    }
    return IngredientLine(**(defaults | overrides))


def test_rejects_a_blank_name() -> None:
    with pytest.raises(ValueError, match="name"):
        _line(name="  ")


def test_rejects_a_negative_quantity() -> None:
    with pytest.raises(ValueError, match="quantity"):
        _line(quantity=-1)


def test_rejects_a_negative_macro() -> None:
    with pytest.raises(ValueError, match="fat_per_100g"):
        _line(fat_per_100g=-1)


def test_grams_follows_the_unit_conversion() -> None:
    assert _line(quantity=2, unit=Unit.TABLESPOON).grams == 30


def test_kcal_scales_with_grams() -> None:
    line = _line(quantity=50, unit=Unit.GRAM, kcal_per_100g=200)
    assert line.kcal() == 100


def test_scaled_multiplies_quantity_and_keeps_macros() -> None:
    line = _line(quantity=100)
    doubled = line.scaled(2)
    assert doubled.quantity == 200
    assert doubled.kcal_per_100g == line.kcal_per_100g


def test_scaled_rejects_a_non_positive_factor() -> None:
    with pytest.raises(ValueError, match="factor"):
        _line().scaled(0)
