from datetime import UTC, datetime
from decimal import Decimal

import pytest

from kitchen_atelier.adapter.outbound.ingestion.ciqual_row_mapper import (
    CiqualFormatError,
    CiqualRowMapper,
)
from kitchen_atelier.domain.ingredient.normalize_search import normalize_search

HEADER: tuple[str, ...] = (
    "alim_code",
    "alim_nom_fr",
    "Energie, Règlement UE N° 1169/2011 (kcal/100 g)",
    "Protéines, N x facteur de Jones (g/100 g)",
    "Glucides (g/100 g)",
    "Lipides (g/100 g)",
)


def _row(*values: object) -> dict[str, object]:
    return dict(zip(HEADER, values, strict=True))


def test_maps_a_well_formed_text_row() -> None:
    mapper = CiqualRowMapper(HEADER)
    row = _row("20000", "Pâtes, cuites", "131", "5,0", "25,0", "1,1")

    food = mapper.map_row(row, datetime.now(UTC))

    assert food is not None
    assert food.identity.ciqual_code == "20000"
    assert food.identity.name == "Pâtes, cuites"
    assert normalize_search(food.identity.name) == "pates, cuites"
    assert food.nutrition.energy.regulation_1169_kcal == 131
    assert food.nutrition.macronutrients.protein_jones_g == 5.0
    assert food.nutrition.macronutrients.carbohydrates_g == 25.0
    assert food.nutrition.macronutrients.fat_g == Decimal("1.1")
    assert food.source == "ciqual"


def test_maps_a_row_with_native_numeric_types_from_a_spreadsheet() -> None:
    mapper = CiqualRowMapper(HEADER)
    row = _row(20000.0, "Pâtes, cuites", 131, 5.0, 25.0, 1.1)

    food = mapper.map_row(row, datetime.now(UTC))

    assert food is not None
    assert food.identity.ciqual_code == "20000"
    assert food.nutrition.energy.regulation_1169_kcal == 131


def test_treats_traces_and_dashes_as_missing() -> None:
    mapper = CiqualRowMapper(HEADER)
    row = _row("20001", "Sel", "0", "traces", "-", "<0,1")

    food = mapper.map_row(row, datetime.now(UTC))

    assert food is not None
    assert food.nutrition.macronutrients.protein_jones_g is None
    assert food.nutrition.macronutrients.carbohydrates_g is None
    assert food.nutrition.macronutrients.fat_g == Decimal("0.1")


def test_skips_a_row_with_no_code_or_name() -> None:
    mapper = CiqualRowMapper(HEADER)
    row = _row("", "", "131", "5,0", "25,0", "1,1")

    assert mapper.map_row(row, datetime.now(UTC)) is None


def test_raises_a_clear_error_when_a_required_column_is_missing() -> None:
    with pytest.raises(CiqualFormatError, match="energie"):
        CiqualRowMapper(("alim_code", "alim_nom_fr"))


def test_has_no_detail_nutrients_when_the_header_carries_only_the_core_columns() -> None:
    mapper = CiqualRowMapper(HEADER)
    row = _row("20000", "Pâtes, cuites", "131", "5,0", "25,0", "1,1")

    food = mapper.map_row(row, datetime.now(UTC))

    assert food is not None
    assert food.identity.scientific_name is None
    assert food.nutrition.macronutrients.water_g is None
    assert food.nutrition.minerals.calcium_mg is None
    assert food.classification.group_name == ""


def test_maps_detail_fields_present_in_the_header() -> None:
    header = (*HEADER, "Eau (g/100 g)", "Calcium (mg/100 g)", "alim_nom_sci", "alim_grp_nom_fr")
    mapper = CiqualRowMapper(header)
    row = dict(
        zip(
            header,
            (
                "20000",
                "Pâtes, cuites",
                "131",
                "5,0",
                "25,0",
                "1,1",
                "68,5",
                "7",
                "Triticum durum",
                "céréales",
            ),
            strict=True,
        )
    )

    food = mapper.map_row(row, datetime.now(UTC))

    assert food is not None
    assert food.identity.scientific_name == "Triticum durum"
    assert food.classification.group_name == "céréales"
    assert food.nutrition.macronutrients.water_g == 68.5
    assert food.nutrition.minerals.calcium_mg == 7


def test_leaves_out_zero_missing_and_dash_detail_values() -> None:
    header = (*HEADER, "Eau (g/100 g)", "alim_nom_sci", "alim_grp_nom_fr")
    mapper = CiqualRowMapper(header)
    row = dict(
        zip(
            header,
            ("20000", "Pâtes, cuites", "131", "5,0", "25,0", "1,1", "0", "", "-"),
            strict=True,
        )
    )

    food = mapper.map_row(row, datetime.now(UTC))

    assert food is not None
    assert food.nutrition.macronutrients.water_g == 0
    assert food.identity.scientific_name is None
    assert food.classification.group_name == ""
