from kitchen_atelier.application.use_case.search_ingredients import SearchIngredients
from tests.support.fakes import FakeIngredientRepository, make_ingredient


async def test_normalizes_the_query_before_searching() -> None:
    repository = FakeIngredientRepository()
    repository.by_code["1"] = make_ingredient("1", "Crème fraîche")

    results = await SearchIngredients(repository).handle("creme")

    assert [food.identity.ciqual_code for food in results] == ["1"]


async def test_returns_nothing_for_a_blank_query() -> None:
    repository = FakeIngredientRepository()
    repository.by_code["1"] = make_ingredient("1", "Crème fraîche")

    assert await SearchIngredients(repository).handle("   ") == []
