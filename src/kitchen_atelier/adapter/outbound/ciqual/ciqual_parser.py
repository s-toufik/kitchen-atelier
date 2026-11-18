import csv
from datetime import datetime
from io import StringIO

from kitchen_atelier.domain.ingredient.ingredient import Ingredient

DELIMITER: str = ";"

CODE_MARKERS: tuple[str, ...] = ("alim_code",)
NAME_MARKERS: tuple[str, ...] = ("alim_nom_fr",)
KCAL_MARKERS: tuple[str, ...] = ("energie", "kcal")
PROTEIN_MARKERS: tuple[str, ...] = ("prot",)
CARB_MARKERS: tuple[str, ...] = ("glucides",)
FAT_MARKERS: tuple[str, ...] = ("lipides",)

_MISSING_VALUES: frozenset[str] = frozenset({"", "-", "traces"})


class CiqualFormatError(Exception):
    pass


def parse_ciqual_csv(raw_text: str, fetched_at: datetime) -> list[Ingredient]:
    reader = csv.reader(StringIO(raw_text), delimiter=DELIMITER)
    try:
        header = next(reader)
    except StopIteration:
        raise CiqualFormatError("CIQUAL file is empty") from None

    columns = _ColumnIndex(header)
    ingredients: list[Ingredient] = []
    for row in reader:
        if not row or len(row) <= columns.max_index:
            continue
        code = row[columns.code].strip()
        name = row[columns.name].strip()
        if not code or not name:
            continue
        ingredients.append(
            Ingredient.from_ciqual_row(
                ciqual_code=code,
                name_fr=name,
                kcal_per_100g=_parse_french_number(row[columns.kcal]),
                protein_per_100g=_parse_french_number(row[columns.protein]),
                carb_per_100g=_parse_french_number(row[columns.carb]),
                fat_per_100g=_parse_french_number(row[columns.fat]),
                updated_at=fetched_at,
            )
        )
    return ingredients


def _parse_french_number(raw: str) -> float:
    cleaned = raw.strip().lower().lstrip("<").strip()
    if cleaned in _MISSING_VALUES:
        return 0.0
    try:
        return float(cleaned.replace(",", "."))
    except ValueError:
        return 0.0


class _ColumnIndex:
    def __init__(self, header: list[str]) -> None:
        normalized = [cell.strip().lower() for cell in header]
        self.code = _find(normalized, CODE_MARKERS)
        self.name = _find(normalized, NAME_MARKERS)
        self.kcal = _find(normalized, KCAL_MARKERS)
        self.protein = _find(normalized, PROTEIN_MARKERS)
        self.carb = _find(normalized, CARB_MARKERS)
        self.fat = _find(normalized, FAT_MARKERS)
        self.max_index = max(self.code, self.name, self.kcal, self.protein, self.carb, self.fat)


def _find(normalized_header: list[str], markers: tuple[str, ...]) -> int:
    for index, cell in enumerate(normalized_header):
        if all(marker in cell for marker in markers):
            return index
    raise CiqualFormatError(f"no CIQUAL column header contains all of {markers!r}")
