from kitchen_atelier.application.use_case.get_or_create_ingredient import GetOrCreateIngredient
from kitchen_atelier.domain.ingredient.normalize_search import normalize_search
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

    assert result.identity.name == "Sel fumé"
    assert normalize_search(result.identity.name) == "sel fume"
    assert result.source == "custom"
    assert result.identity.ciqual_code.startswith("custom:")
    assert repository.by_code[result.identity.ciqual_code] == result


async def test_clamps_negative_macros_to_zero() -> None:
    repository = FakeIngredientRepository()

    result = await GetOrCreateIngredient(repository).handle(
        "Eau", kcal_per_100g=-5, protein_per_100g=-1, carb_per_100g=-1, fat_per_100g=-1
    )

    assert result.nutrition.energy.regulation_1169_kcal == 0
    assert result.nutrition.macronutrients.protein_jones_g == 0
    assert result.nutrition.macronutrients.carbohydrates_g == 0
    assert result.nutrition.macronutrients.fat_g == 0
