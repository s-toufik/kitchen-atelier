import logging
from datetime import UTC, datetime

from kitchen_atelier.application.use_case.refresh_ingredient_catalog import (
    RefreshIngredientCatalog,
)
from kitchen_atelier.domain.ingredient.ingredient import Ingredient
from tests.support.fakes import FakeIngredientRepository, FakeIngredientSource


def _ingredient(ciqual_code: str) -> Ingredient:
    return Ingredient.from_ciqual_row(
        ciqual_code=ciqual_code,
        name_fr="Riz",
        kcal_per_100g=130,
        protein_per_100g=2.7,
        carb_per_100g=28.0,
        fat_per_100g=0.3,
        updated_at=datetime.now(UTC),
    )


async def test_upserts_everything_the_source_returns() -> None:
    repository = FakeIngredientRepository()
    source = FakeIngredientSource([_ingredient("1"), _ingredient("2")])

    changed = await RefreshIngredientCatalog(source, repository, logging.getLogger(__name__)).handle()

    assert changed == 2
    assert set(repository.by_code) == {"1", "2"}


async def test_an_empty_source_changes_nothing() -> None:
    repository = FakeIngredientRepository()
    source = FakeIngredientSource([])

    changed = await RefreshIngredientCatalog(source, repository, logging.getLogger(__name__)).handle()

    assert changed == 0
    assert repository.by_code == {}
