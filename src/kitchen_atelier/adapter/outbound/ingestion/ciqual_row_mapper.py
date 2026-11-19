from collections.abc import Iterable
from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import Any

from kitchen_atelier.domain.ingredient.energy import Energy
from kitchen_atelier.domain.ingredient.fatty_acids import FattyAcids
from kitchen_atelier.domain.ingredient.food import Food
from kitchen_atelier.domain.ingredient.food_classification import FoodClassification
from kitchen_atelier.domain.ingredient.food_identity import FoodIdentity
from kitchen_atelier.domain.ingredient.macronutrients import Macronutrients
from kitchen_atelier.domain.ingredient.minerals import Minerals
from kitchen_atelier.domain.ingredient.nutritional_composition import NutritionalComposition
from kitchen_atelier.domain.ingredient.sugars import Sugars
from kitchen_atelier.domain.ingredient.vitamins import Vitamins

SOURCE: str = "ciqual"
SOURCE_VERSION: str = "Ciqual 2020"

CODE_MARKERS: tuple[str, ...] = ("alim_code",)
NAME_MARKERS: tuple[str, ...] = ("alim_nom_fr",)
KCAL_MARKERS: tuple[str, ...] = ("energie", "kcal")
PROTEIN_MARKERS: tuple[str, ...] = ("prot",)
CARB_MARKERS: tuple[str, ...] = ("glucides",)
FAT_MARKERS: tuple[str, ...] = ("lipides",)

_MISSING_VALUES: frozenset[str] = frozenset({"", "-", "traces"})

_TEXT_FIELDS: tuple[tuple[str, str], ...] = (
    ("scientific_name", "alim_nom_sci"),
    ("group_code", "alim_grp_code"),
    ("subgroup_code", "alim_ssgrp_code"),
    ("sub_subgroup_code", "alim_ssssgrp_code"),
    ("group_name", "alim_grp_nom_fr"),
    ("subgroup_name", "alim_ssgrp_nom_fr"),
    ("sub_subgroup_name", "alim_ssssgrp_nom_fr"),
)

_NUTRIENT_FIELDS: tuple[tuple[str, str], ...] = (
    ("regulation_1169_kj", "Energie, Règlement UE N° 1169/2011 (kJ/100 g)"),
    ("jones_with_fiber_kj", "Energie, N x facteur Jones, avec fibres (kJ/100 g)"),
    ("jones_with_fiber_kcal", "Energie, N x facteur Jones, avec fibres (kcal/100 g)"),
    ("water_g", "Eau (g/100 g)"),
    ("protein_6_25_g", "Protéines, N x 6.25 (g/100 g)"),
    ("total_sugars_g", "Sucres (g/100 g)"),
    ("fructose_g", "Fructose (g/100 g)"),
    ("galactose_g", "Galactose (g/100 g)"),
    ("glucose_g", "Glucose (g/100 g)"),
    ("lactose_g", "Lactose (g/100 g)"),
    ("maltose_g", "Maltose (g/100 g)"),
    ("sucrose_g", "Saccharose (g/100 g)"),
    ("starch_g", "Amidon (g/100 g)"),
    ("dietary_fiber_g", "Fibres alimentaires (g/100 g)"),
    ("total_polyols_g", "Polyols totaux (g/100 g)"),
    ("ash_g", "Cendres (g/100 g)"),
    ("alcohol_g", "Alcool (g/100 g)"),
    ("organic_acids_g", "Acides organiques (g/100 g)"),
    ("saturated_g", "AG saturés (g/100 g)"),
    ("monounsaturated_g", "AG monoinsaturés (g/100 g)"),
    ("polyunsaturated_g", "AG polyinsaturés (g/100 g)"),
    ("butyric_acid_4_0_g", "AG 4:0, butyrique (g/100 g)"),
    ("caproic_acid_6_0_g", "AG 6:0, caproïque (g/100 g)"),
    ("caprylic_acid_8_0_g", "AG 8:0, caprylique (g/100 g)"),
    ("capric_acid_10_0_g", "AG 10:0, caprique (g/100 g)"),
    ("lauric_acid_12_0_g", "AG 12:0, laurique (g/100 g)"),
    ("myristic_acid_14_0_g", "AG 14:0, myristique (g/100 g)"),
    ("palmitic_acid_16_0_g", "AG 16:0, palmitique (g/100 g)"),
    ("stearic_acid_18_0_g", "AG 18:0, stéarique (g/100 g)"),
    ("oleic_acid_18_1_g", "AG 18:1 9c (n-9), oléique (g/100 g)"),
    ("linoleic_acid_18_2_g", "AG 18:2 9c,12c (n-6), linoléique (g/100 g)"),
    ("alpha_linolenic_acid_18_3_g", "AG 18:3 c9,c12,c15 (n-3), alpha-linolénique (g/100 g)"),
    ("arachidonic_acid_20_4_g", "AG 20:4 5c,8c,11c,14c (n-6), arachidonique (g/100 g)"),
    ("epa_20_5_g", "AG 20:5 5c,8c,11c,14c,17c (n-3) EPA (g/100 g)"),
    ("dha_22_6_g", "AG 22:6 4c,7c,10c,13c,16c,19c (n-3) DHA (g/100 g)"),
    ("cholesterol_mg", "Cholestérol (mg/100 g)"),
    ("sodium_chloride_g", "Sel chlorure de sodium (g/100 g)"),
    ("calcium_mg", "Calcium (mg/100 g)"),
    ("chloride_mg", "Chlorure (mg/100 g)"),
    ("copper_mg", "Cuivre (mg/100 g)"),
    ("iron_mg", "Fer (mg/100 g)"),
    ("iodine_ug", "Iode (µg/100 g)"),
    ("magnesium_mg", "Magnésium (mg/100 g)"),
    ("manganese_mg", "Manganèse (mg/100 g)"),
    ("phosphorus_mg", "Phosphore (mg/100 g)"),
    ("potassium_mg", "Potassium (mg/100 g)"),
    ("selenium_ug", "Sélénium (µg/100 g)"),
    ("sodium_mg", "Sodium (mg/100 g)"),
    ("zinc_mg", "Zinc (mg/100 g)"),
    ("retinol_ug", "Rétinol (µg/100 g)"),
    ("beta_carotene_ug", "Beta-Carotène (µg/100 g)"),
    ("vitamin_d_ug", "Vitamine D (µg/100 g)"),
    ("vitamin_e_mg", "Vitamine E (mg/100 g)"),
    ("vitamin_k1_ug", "Vitamine K1 (µg/100 g)"),
    ("vitamin_k2_ug", "Vitamine K2 (µg/100 g)"),
    ("vitamin_c_mg", "Vitamine C (mg/100 g)"),
    ("vitamin_b1_mg", "Vitamine B1 ou Thiamine (mg/100 g)"),
    ("vitamin_b2_mg", "Vitamine B2 ou Riboflavine (mg/100 g)"),
    ("vitamin_b3_mg", "Vitamine B3 ou PP ou Niacine (mg/100 g)"),
    ("vitamin_b5_mg", "Vitamine B5 ou Acide pantothénique (mg/100 g)"),
    ("vitamin_b6_mg", "Vitamine B6 (mg/100 g)"),
    ("vitamin_b9_ug", "Vitamine B9 ou Folates totaux (µg/100 g)"),
    ("vitamin_b12_ug", "Vitamine B12 (µg/100 g)"),
)


class CiqualFormatError(Exception):
    pass


class CiqualRowMapper:
    def __init__(self, header: Iterable[str]) -> None:
        fuzzy = {str(key).strip().lower(): key for key in header}
        self._code_key = _find_column(fuzzy, CODE_MARKERS)
        self._name_key = _find_column(fuzzy, NAME_MARKERS)
        self._kcal_key = _find_column(fuzzy, KCAL_MARKERS)
        self._protein_key = _find_column(fuzzy, PROTEIN_MARKERS)
        self._carb_key = _find_column(fuzzy, CARB_MARKERS)
        self._fat_key = _find_column(fuzzy, FAT_MARKERS)

        exact = {_normalize_exact(str(key)): key for key in header}
        self._text_columns = {
            field: column
            for field, expected in _TEXT_FIELDS
            if (column := exact.get(_normalize_exact(expected))) is not None
        }
        self._nutrient_columns = {
            field: column
            for field, expected in _NUTRIENT_FIELDS
            if (column := exact.get(_normalize_exact(expected))) is not None
        }

    def map_row(self, row: dict[str, Any], fetched_at: datetime) -> Food | None:
        code = _clean_text(row.get(self._code_key))
        name = _clean_text(row.get(self._name_key))
        if not code or not name:
            return None

        text = {field: _clean_text(row.get(column)) for field, column in self._text_columns.items()}
        nutrient = {
            field: _parse_decimal(row.get(column)) for field, column in self._nutrient_columns.items()
        }

        return Food(
            identity=FoodIdentity(
                ciqual_code=code,
                name=name,
                scientific_name=text.get("scientific_name") or None,
            ),
            classification=FoodClassification(
                group_code=text.get("group_code", ""),
                subgroup_code=text.get("subgroup_code", ""),
                sub_subgroup_code=text.get("sub_subgroup_code", ""),
                group_name=text.get("group_name", ""),
                subgroup_name=text.get("subgroup_name", ""),
                sub_subgroup_name=text.get("sub_subgroup_name", ""),
            ),
            nutrition=NutritionalComposition(
                energy=Energy(
                    regulation_1169_kj=nutrient.get("regulation_1169_kj"),
                    regulation_1169_kcal=_parse_decimal(row.get(self._kcal_key)),
                    jones_with_fiber_kj=nutrient.get("jones_with_fiber_kj"),
                    jones_with_fiber_kcal=nutrient.get("jones_with_fiber_kcal"),
                ),
                macronutrients=Macronutrients(
                    water_g=nutrient.get("water_g"),
                    protein_jones_g=_parse_decimal(row.get(self._protein_key)),
                    protein_6_25_g=nutrient.get("protein_6_25_g"),
                    carbohydrates_g=_parse_decimal(row.get(self._carb_key)),
                    fat_g=_parse_decimal(row.get(self._fat_key)),
                    dietary_fiber_g=nutrient.get("dietary_fiber_g"),
                    total_polyols_g=nutrient.get("total_polyols_g"),
                    ash_g=nutrient.get("ash_g"),
                    alcohol_g=nutrient.get("alcohol_g"),
                    organic_acids_g=nutrient.get("organic_acids_g"),
                ),
                sugars=Sugars(
                    total_sugars_g=nutrient.get("total_sugars_g"),
                    fructose_g=nutrient.get("fructose_g"),
                    galactose_g=nutrient.get("galactose_g"),
                    glucose_g=nutrient.get("glucose_g"),
                    lactose_g=nutrient.get("lactose_g"),
                    maltose_g=nutrient.get("maltose_g"),
                    sucrose_g=nutrient.get("sucrose_g"),
                    starch_g=nutrient.get("starch_g"),
                ),
                fatty_acids=FattyAcids(
                    saturated_g=nutrient.get("saturated_g"),
                    monounsaturated_g=nutrient.get("monounsaturated_g"),
                    polyunsaturated_g=nutrient.get("polyunsaturated_g"),
                    butyric_acid_4_0_g=nutrient.get("butyric_acid_4_0_g"),
                    caproic_acid_6_0_g=nutrient.get("caproic_acid_6_0_g"),
                    caprylic_acid_8_0_g=nutrient.get("caprylic_acid_8_0_g"),
                    capric_acid_10_0_g=nutrient.get("capric_acid_10_0_g"),
                    lauric_acid_12_0_g=nutrient.get("lauric_acid_12_0_g"),
                    myristic_acid_14_0_g=nutrient.get("myristic_acid_14_0_g"),
                    palmitic_acid_16_0_g=nutrient.get("palmitic_acid_16_0_g"),
                    stearic_acid_18_0_g=nutrient.get("stearic_acid_18_0_g"),
                    oleic_acid_18_1_g=nutrient.get("oleic_acid_18_1_g"),
                    linoleic_acid_18_2_g=nutrient.get("linoleic_acid_18_2_g"),
                    alpha_linolenic_acid_18_3_g=nutrient.get("alpha_linolenic_acid_18_3_g"),
                    arachidonic_acid_20_4_g=nutrient.get("arachidonic_acid_20_4_g"),
                    epa_20_5_g=nutrient.get("epa_20_5_g"),
                    dha_22_6_g=nutrient.get("dha_22_6_g"),
                ),
                minerals=Minerals(
                    cholesterol_mg=nutrient.get("cholesterol_mg"),
                    sodium_chloride_g=nutrient.get("sodium_chloride_g"),
                    calcium_mg=nutrient.get("calcium_mg"),
                    chloride_mg=nutrient.get("chloride_mg"),
                    copper_mg=nutrient.get("copper_mg"),
                    iron_mg=nutrient.get("iron_mg"),
                    iodine_ug=nutrient.get("iodine_ug"),
                    magnesium_mg=nutrient.get("magnesium_mg"),
                    manganese_mg=nutrient.get("manganese_mg"),
                    phosphorus_mg=nutrient.get("phosphorus_mg"),
                    potassium_mg=nutrient.get("potassium_mg"),
                    selenium_ug=nutrient.get("selenium_ug"),
                    sodium_mg=nutrient.get("sodium_mg"),
                    zinc_mg=nutrient.get("zinc_mg"),
                ),
                vitamins=Vitamins(
                    retinol_ug=nutrient.get("retinol_ug"),
                    beta_carotene_ug=nutrient.get("beta_carotene_ug"),
                    vitamin_d_ug=nutrient.get("vitamin_d_ug"),
                    vitamin_e_mg=nutrient.get("vitamin_e_mg"),
                    vitamin_k1_ug=nutrient.get("vitamin_k1_ug"),
                    vitamin_k2_ug=nutrient.get("vitamin_k2_ug"),
                    vitamin_c_mg=nutrient.get("vitamin_c_mg"),
                    vitamin_b1_mg=nutrient.get("vitamin_b1_mg"),
                    vitamin_b2_mg=nutrient.get("vitamin_b2_mg"),
                    vitamin_b3_mg=nutrient.get("vitamin_b3_mg"),
                    vitamin_b5_mg=nutrient.get("vitamin_b5_mg"),
                    vitamin_b6_mg=nutrient.get("vitamin_b6_mg"),
                    vitamin_b9_ug=nutrient.get("vitamin_b9_ug"),
                    vitamin_b12_ug=nutrient.get("vitamin_b12_ug"),
                ),
            ),
            source=SOURCE,
            source_version=SOURCE_VERSION,
            updated_at=fetched_at,
        )


def _find_column(normalized_header: dict[str, str], markers: tuple[str, ...]) -> str:
    for normalized_key, original_key in normalized_header.items():
        if all(marker in normalized_key for marker in markers):
            return original_key
    raise CiqualFormatError(f"no column header contains all of {markers!r}")


def _normalize_exact(header: str) -> str:
    return " ".join(header.strip().lower().split())


def _clean_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    text = str(value).strip()
    return "" if text in _MISSING_VALUES else text


def _parse_decimal(value: Any) -> Decimal | None:
    if value is None:
        return None
    if isinstance(value, int | float):
        return Decimal(str(value))
    cleaned = str(value).strip().lower().lstrip("<").strip()
    if cleaned in _MISSING_VALUES:
        return None
    try:
        return Decimal(cleaned.replace(",", "."))
    except InvalidOperation:
        return None
