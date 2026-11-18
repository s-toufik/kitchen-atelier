from datetime import UTC, datetime

import pytest

from kitchen_atelier.adapter.outbound.ciqual.ciqual_parser import (
    CiqualFormatError,
    parse_ciqual_csv,
)

HEADER = (
    "alim_code;alim_nom_fr;"
    "Energie, Règlement UE N° 1169/2011 (kcal/100 g);"
    "Protéines, N x 6.25 (g/100 g);"
    "Glucides (g/100 g);"
    "Lipides (g/100 g)"
)


def test_parses_a_well_formed_row() -> None:
    csv_text = HEADER + "\n" + "20000;Pâtes, cuites;131;5,0;25,0;1,1"

    ingredients = parse_ciqual_csv(csv_text, datetime.now(UTC))

    assert len(ingredients) == 1
    ingredient = ingredients[0]
    assert ingredient.ciqual_code == "20000"
    assert ingredient.name_fr == "Pâtes, cuites"
    assert ingredient.kcal_per_100g == 131
    assert ingredient.protein_per_100g == 5.0
    assert ingredient.carb_per_100g == 25.0
    assert ingredient.fat_per_100g == 1.1


def test_treats_traces_and_dashes_as_zero() -> None:
    csv_text = HEADER + "\n" + "20001;Sel;0;traces;-;<0,1"

    ingredient = parse_ciqual_csv(csv_text, datetime.now(UTC))[0]

    assert ingredient.protein_per_100g == 0.0
    assert ingredient.carb_per_100g == 0.0
    assert ingredient.fat_per_100g == 0.1


def test_skips_a_row_with_no_code_or_name() -> None:
    csv_text = HEADER + "\n" + ";;131;5,0;25,0;1,1"

    assert parse_ciqual_csv(csv_text, datetime.now(UTC)) == []


def test_raises_a_clear_error_when_a_required_column_is_missing() -> None:
    bad_header = "alim_code;alim_nom_fr\n20000;Pâtes"

    with pytest.raises(CiqualFormatError, match="energie"):
        parse_ciqual_csv(bad_header, datetime.now(UTC))


def test_raises_on_an_empty_file() -> None:
    with pytest.raises(CiqualFormatError, match="empty"):
        parse_ciqual_csv("", datetime.now(UTC))
