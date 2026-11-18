from datetime import UTC, datetime

from kitchen_atelier.application.use_case.search_ingredients import SearchIngredients
from kitchen_atelier.domain.ingredient.ingredient import Ingredient
from tests.support.fakes import FakeIngredientRepository


def _ingredient(name_fr: str, ciqual_code: str) -> Ingredient:
    return Ingredient.from_ciqual_row(
        ciqual_code=ciqual_code,
        name_fr=name_fr,
        kcal_per_100g=0,
        protein_per_100g=0,
        carb_per_100g=0,
        fat_per_100g=0,
        updated_at=datetime.now(UTC),
    )


async def test_normalizes_the_query_before_searching() -> None:
    repository = FakeIngredientRepository()
    repository.by_code["1"] = _ingredient("Crème fraîche", "1")

    results = await SearchIngredients(repository).handle("creme")

    assert [ingredient.ciqual_code for ingredient in results] == ["1"]


async def test_returns_nothing_for_a_blank_query() -> None:
    repository = FakeIngredientRepository()
    repository.by_code["1"] = _ingredient("Crème fraîche", "1")

    assert await SearchIngredients(repository).handle("   ") == []
