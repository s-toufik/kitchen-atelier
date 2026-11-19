from kitchen_atelier.application.use_case.list_ingredients import ListIngredients
from tests.support.fakes import FakeIngredientRepository, make_ingredient


async def test_lists_ingredients_ordered_by_name() -> None:
    repository = FakeIngredientRepository()
    repository.by_code["1"] = make_ingredient("1", "Riz")
    repository.by_code["2"] = make_ingredient("2", "Ail")

    results = await ListIngredients(repository).handle()

    assert [food.identity.name for food in results] == ["Ail", "Riz"]


async def test_paginates_with_limit_and_offset() -> None:
    repository = FakeIngredientRepository()
    repository.by_code["1"] = make_ingredient("1", "Ail")
    repository.by_code["2"] = make_ingredient("2", "Beurre")
    repository.by_code["3"] = make_ingredient("3", "Carotte")

    results = await ListIngredients(repository).handle(limit=1, offset=1)

    assert [food.identity.name for food in results] == ["Beurre"]
