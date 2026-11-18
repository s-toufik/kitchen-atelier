import logging

from kitchen_atelier.application.use_case.refresh_ingredient_catalog import (
    RefreshIngredientCatalog,
)
from tests.support.fakes import FakeIngredientRepository, FakeIngredientSource, make_ingredient


async def test_upserts_everything_the_source_returns() -> None:
    repository = FakeIngredientRepository()
    source = FakeIngredientSource([make_ingredient("1"), make_ingredient("2")])

    changed = await RefreshIngredientCatalog(source, repository, logging.getLogger(__name__)).handle()

    assert changed == 2
    assert set(repository.by_code) == {"1", "2"}


async def test_an_empty_source_changes_nothing() -> None:
    repository = FakeIngredientRepository()
    source = FakeIngredientSource([])

    changed = await RefreshIngredientCatalog(source, repository, logging.getLogger(__name__)).handle()

    assert changed == 0
    assert repository.by_code == {}
