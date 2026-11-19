import json
from decimal import Decimal

from kitchen_atelier.adapter.outbound.sql.ingredient_repository import (
    _nutrition_from_json,
    _nutrition_to_json,
)
from kitchen_atelier.domain.ingredient.energy import Energy
from kitchen_atelier.domain.ingredient.fatty_acids import FattyAcids
from kitchen_atelier.domain.ingredient.macronutrients import Macronutrients
from kitchen_atelier.domain.ingredient.minerals import Minerals
from kitchen_atelier.domain.ingredient.nutritional_composition import NutritionalComposition
from kitchen_atelier.domain.ingredient.sugars import Sugars
from kitchen_atelier.domain.ingredient.vitamins import Vitamins


def _composition() -> NutritionalComposition:
    return NutritionalComposition(
        energy=Energy(regulation_1169_kcal=Decimal("80.5")),
        macronutrients=Macronutrients(protein_jones_g=Decimal("2.16"), fat_g=Decimal("0.18")),
        sugars=Sugars(fructose_g=Decimal("0.15")),
        fatty_acids=FattyAcids(saturated_g=Decimal("0.038")),
        minerals=Minerals(iron_mg=Decimal("0.91")),
        vitamins=Vitamins(vitamin_c_mg=Decimal("18.9")),
    )


def test_round_trips_through_json_without_losing_precision() -> None:
    composition = _composition()

    encoded = json.loads(json.dumps(_nutrition_to_json(composition)))
    decoded = _nutrition_from_json(encoded)

    assert decoded == composition


def test_encodes_decimals_as_strings_and_nones_stay_none() -> None:
    encoded = _nutrition_to_json(_composition())

    assert encoded["energy"]["regulation_1169_kcal"] == "80.5"
    assert encoded["energy"]["regulation_1169_kj"] is None


def test_decodes_a_missing_section_as_all_absent_nutrients() -> None:
    decoded = _nutrition_from_json({})

    assert decoded == NutritionalComposition(
        energy=Energy(),
        macronutrients=Macronutrients(),
        sugars=Sugars(),
        fatty_acids=FattyAcids(),
        minerals=Minerals(),
        vitamins=Vitamins(),
    )
