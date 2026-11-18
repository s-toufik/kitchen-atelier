from datetime import UTC, datetime

import pytest

from kitchen_atelier.domain.ingredient.ingredient import Ingredient, normalize_search


def test_normalize_search_strips_accents_and_case() -> None:
    assert normalize_search("Crème fraîche") == "creme fraiche"


def test_from_ciqual_row_derives_the_search_key() -> None:
    ingredient = Ingredient.from_ciqual_row(
        ciqual_code="20000",
        name_fr="Pâtes, cuites",
        kcal_per_100g=131,
        protein_per_100g=5.0,
        carb_per_100g=25.0,
        fat_per_100g=1.1,
        updated_at=datetime.now(UTC),
    )
    assert ingredient.name_search == "pates, cuites"
    assert ingredient.source == "ciqual"


def test_rejects_a_negative_macro() -> None:
    with pytest.raises(ValueError, match="kcal_per_100g"):
        Ingredient(
            ciqual_code="1",
            name_fr="Test",
            name_search="test",
            kcal_per_100g=-1,
            protein_per_100g=0,
            carb_per_100g=0,
            fat_per_100g=0,
            source="ciqual",
            updated_at=datetime.now(UTC),
        )
