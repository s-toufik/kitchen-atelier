from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class FoodIdentity:
    ciqual_code: str
    name: str
    scientific_name: str | None = None
