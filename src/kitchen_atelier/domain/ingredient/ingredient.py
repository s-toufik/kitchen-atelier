import unicodedata
from dataclasses import dataclass
from datetime import datetime

CIQUAL_SOURCE: str = "ciqual"

_NON_NEGATIVE_FIELDS: tuple[str, ...] = (
    "kcal_per_100g",
    "protein_per_100g",
    "carb_per_100g",
    "fat_per_100g",
)


def normalize_search(name: str) -> str:
    """Accent/case-insensitive key so 'crème' and 'creme' both match a search for 'creme'."""
    folded = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode("ascii")
    return folded.strip().lower()


@dataclass(frozen=True, slots=True)
class Ingredient:
    """A catalog entry: macros per 100g for one French ingredient, usually from CIQUAL."""

    ciqual_code: str
    name_fr: str
    name_search: str
    kcal_per_100g: float
    protein_per_100g: float
    carb_per_100g: float
    fat_per_100g: float
    source: str
    updated_at: datetime

    def __post_init__(self) -> None:
        if not self.ciqual_code.strip():
            raise ValueError("an ingredient needs a ciqual_code")
        if not self.name_fr.strip():
            raise ValueError("an ingredient needs a French name")
        for field_name in _NON_NEGATIVE_FIELDS:
            if getattr(self, field_name) < 0:
                raise ValueError(f"ingredient {self.name_fr!r}: {field_name} must be 0 or more")

    @classmethod
    def from_ciqual_row(
        cls,
        *,
        ciqual_code: str,
        name_fr: str,
        kcal_per_100g: float,
        protein_per_100g: float,
        carb_per_100g: float,
        fat_per_100g: float,
        updated_at: datetime,
    ) -> Ingredient:
        return cls(
            ciqual_code=ciqual_code,
            name_fr=name_fr,
            name_search=normalize_search(name_fr),
            kcal_per_100g=kcal_per_100g,
            protein_per_100g=protein_per_100g,
            carb_per_100g=carb_per_100g,
            fat_per_100g=fat_per_100g,
            source=CIQUAL_SOURCE,
            updated_at=updated_at,
        )
