from kitchen_atelier.domain.recipe.unit import Unit, to_grams


def test_gram_is_identity() -> None:
    assert to_grams(250, Unit.GRAM) == 250


def test_kilogram_converts_to_grams() -> None:
    assert to_grams(1.5, Unit.KILOGRAM) == 1500


def test_tablespoon_is_fifteen_grams() -> None:
    assert to_grams(2, Unit.TABLESPOON) == 30


def test_pinch_is_half_a_gram() -> None:
    assert to_grams(1, Unit.PINCH) == 0.5
