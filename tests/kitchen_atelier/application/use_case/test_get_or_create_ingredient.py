from kitchen_atelier.application.use_case.get_or_create_ingredient import GetOrCreateIngredient
from tests.support.fakes import FakeIngredientRepository, make_ingredient


async def test_returns_the_existing_ingredient_when_the_name_matches() -> None:
    repository = FakeIngredientRepository()
    existing = make_ingredient("1", "Crème fraîche", kcal_per_100g=200)
    repository.by_code["1"] = existing

    result = await GetOrCreateIngredient(repository).handle(
        "crème fraîche", kcal_per_100g=0, protein_per_100g=0, carb_per_100g=0, fat_per_100g=0
    )

    assert result == existing


async def test_creates_a_custom_ingredient_when_no_match_exists() -> None:
    repository = FakeIngredientRepository()

    result = await GetOrCreateIngredient(repository).handle(
        "Sel fumé",
        kcal_per_100g=0,
        protein_per_100g=0,
        carb_per_100g=0,
        fat_per_100g=0,
    )

    assert result.name_fr == "Sel fumé"
    assert result.name_search == "sel fume"
    assert result.source == "custom"
    assert result.ciqual_code.startswith("custom:")
    assert repository.by_code[result.ciqual_code] == result


async def test_clamps_negative_macros_to_zero() -> None:
    repository = FakeIngredientRepository()

    result = await GetOrCreateIngredient(repository).handle(
        "Eau", kcal_per_100g=-5, protein_per_100g=-1, carb_per_100g=-1, fat_per_100g=-1
    )

    assert result.kcal_per_100g == 0
    assert result.protein_per_100g == 0
    assert result.carb_per_100g == 0
    assert result.fat_per_100g == 0
