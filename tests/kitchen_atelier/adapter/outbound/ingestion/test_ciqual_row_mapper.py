from datetime import UTC, datetime

import pytest

from kitchen_atelier.adapter.outbound.ingestion.ciqual_row_mapper import (
    CiqualFormatError,
    CiqualRowMapper,
)

HEADER: tuple[str, ...] = (
    "alim_code",
    "alim_nom_fr",
    "Energie, Règlement UE N° 1169/2011 (kcal/100 g)",
    "Protéines, N x 6.25 (g/100 g)",
    "Glucides (g/100 g)",
    "Lipides (g/100 g)",
)


def _row(*values: object) -> dict[str, object]:
    return dict(zip(HEADER, values, strict=True))


def test_maps_a_well_formed_text_row() -> None:
    mapper = CiqualRowMapper(HEADER)
    row = _row("20000", "Pâtes, cuites", "131", "5,0", "25,0", "1,1")

    ingredient = mapper.map_row(row, datetime.now(UTC))

    assert ingredient is not None
    assert ingredient.ciqual_code == "20000"
    assert ingredient.name_fr == "Pâtes, cuites"
    assert ingredient.name_search == "pates, cuites"
    assert ingredient.kcal_per_100g == 131
    assert ingredient.protein_per_100g == 5.0
    assert ingredient.carb_per_100g == 25.0
    assert ingredient.fat_per_100g == 1.1
    assert ingredient.source == "ciqual"


def test_maps_a_row_with_native_numeric_types_from_a_spreadsheet() -> None:
    mapper = CiqualRowMapper(HEADER)
    row = _row(20000.0, "Pâtes, cuites", 131, 5.0, 25.0, 1.1)

    ingredient = mapper.map_row(row, datetime.now(UTC))

    assert ingredient is not None
    assert ingredient.ciqual_code == "20000"
    assert ingredient.kcal_per_100g == 131


def test_treats_traces_and_dashes_as_zero() -> None:
    mapper = CiqualRowMapper(HEADER)
    row = _row("20001", "Sel", "0", "traces", "-", "<0,1")

    ingredient = mapper.map_row(row, datetime.now(UTC))

    assert ingredient is not None
    assert ingredient.protein_per_100g == 0.0
    assert ingredient.carb_per_100g == 0.0
    assert ingredient.fat_per_100g == 0.1


def test_skips_a_row_with_no_code_or_name() -> None:
    mapper = CiqualRowMapper(HEADER)
    row = _row("", "", "131", "5,0", "25,0", "1,1")

    assert mapper.map_row(row, datetime.now(UTC)) is None


def test_raises_a_clear_error_when_a_required_column_is_missing() -> None:
    with pytest.raises(CiqualFormatError, match="energie"):
        CiqualRowMapper(("alim_code", "alim_nom_fr"))
