from collections.abc import Iterable
from datetime import datetime
from typing import Any

from kitchen_atelier.domain.ingredient.ingredient import Ingredient, normalize_search

SOURCE: str = "ciqual"

CODE_MARKERS: tuple[str, ...] = ("alim_code",)
NAME_MARKERS: tuple[str, ...] = ("alim_nom_fr",)
KCAL_MARKERS: tuple[str, ...] = ("energie", "kcal")
PROTEIN_MARKERS: tuple[str, ...] = ("prot",)
CARB_MARKERS: tuple[str, ...] = ("glucides",)
FAT_MARKERS: tuple[str, ...] = ("lipides",)

_MISSING_VALUES: frozenset[str] = frozenset({"", "-", "traces"})


class CiqualFormatError(Exception):
    pass


class CiqualRowMapper:
    def __init__(self, header: Iterable[str]) -> None:
        normalized = {str(key).strip().lower(): key for key in header}
        self._code_key = _find_column(normalized, CODE_MARKERS)
        self._name_key = _find_column(normalized, NAME_MARKERS)
        self._kcal_key = _find_column(normalized, KCAL_MARKERS)
        self._protein_key = _find_column(normalized, PROTEIN_MARKERS)
        self._carb_key = _find_column(normalized, CARB_MARKERS)
        self._fat_key = _find_column(normalized, FAT_MARKERS)

    def map_row(self, row: dict[str, Any], fetched_at: datetime) -> Ingredient | None:
        code = _clean_text(row.get(self._code_key))
        name = _clean_text(row.get(self._name_key))
        if not code or not name:
            return None

        return Ingredient(
            ciqual_code=code,
            name_fr=name,
            name_search=normalize_search(name),
            kcal_per_100g=_parse_number(row.get(self._kcal_key)),
            protein_per_100g=_parse_number(row.get(self._protein_key)),
            carb_per_100g=_parse_number(row.get(self._carb_key)),
            fat_per_100g=_parse_number(row.get(self._fat_key)),
            source=SOURCE,
            updated_at=fetched_at,
        )


def _find_column(normalized_header: dict[str, str], markers: tuple[str, ...]) -> str:
    for normalized_key, original_key in normalized_header.items():
        if all(marker in normalized_key for marker in markers):
            return original_key
    raise CiqualFormatError(f"no column header contains all of {markers!r}")


def _clean_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value).strip()


def _parse_number(value: Any) -> float:
    if value is None:
        return 0.0
    if isinstance(value, int | float):
        return float(value)
    cleaned = str(value).strip().lower().lstrip("<").strip()
    if cleaned in _MISSING_VALUES:
        return 0.0
    try:
        return float(cleaned.replace(",", "."))
    except ValueError:
        return 0.0
