from enum import StrEnum


class Unit(StrEnum):
    GRAM = "g"
    KILOGRAM = "kg"
    MILLILITER = "ml"
    CENTILITER = "cl"
    LITER = "L"
    TABLESPOON = "càs"
    TEASPOON = "càc"
    PINCH = "pincée"
    PIECE = "pièce"


GRAM_EQUIVALENT: dict[Unit, float] = {
    Unit.GRAM: 1.0,
    Unit.KILOGRAM: 1000.0,
    Unit.MILLILITER: 1.0,
    Unit.CENTILITER: 10.0,
    Unit.LITER: 1000.0,
    Unit.TABLESPOON: 15.0,
    Unit.TEASPOON: 5.0,
    Unit.PINCH: 0.5,
    Unit.PIECE: 50.0,
}


def to_grams(quantity: float, unit: Unit) -> float:
    return quantity * GRAM_EQUIVALENT[unit]
