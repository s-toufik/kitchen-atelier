from collections.abc import Iterable
from dataclasses import asdict
from decimal import Decimal
from typing import Any

from psycopg.types.json import Jsonb
from pycraftcore.repository.port import AsyncRepository

from kitchen_atelier.domain.ingredient.energy import Energy
from kitchen_atelier.domain.ingredient.fatty_acids import FattyAcids
from kitchen_atelier.domain.ingredient.food import Food
from kitchen_atelier.domain.ingredient.food_classification import FoodClassification
from kitchen_atelier.domain.ingredient.food_identity import FoodIdentity
from kitchen_atelier.domain.ingredient.macronutrients import Macronutrients
from kitchen_atelier.domain.ingredient.minerals import Minerals
from kitchen_atelier.domain.ingredient.normalize_search import normalize_search
from kitchen_atelier.domain.ingredient.nutritional_composition import NutritionalComposition
from kitchen_atelier.domain.ingredient.sugars import Sugars
from kitchen_atelier.domain.ingredient.vitamins import Vitamins

SCHEMA: str = "kitchen"
TABLE: str = "ingredients"
_COLUMNS: str = (
    "ciqual_code, name_fr, name_search, scientific_name, "
    "group_code, subgroup_code, sub_subgroup_code, group_name, subgroup_name, sub_subgroup_name, "
    "kcal_per_100g, protein_per_100g, carb_per_100g, fat_per_100g, "
    "source, source_version, updated_at, nutrition"
)


class SqlIngredientRepository:
    def __init__(self, repository: AsyncRepository) -> None:
        self._repository = repository

    async def search(self, query: str, limit: int = 20) -> list[Food]:
        rows = await self._repository.execute(
            f"SELECT {_COLUMNS} FROM {SCHEMA}.{TABLE} "
            "WHERE name_search LIKE %s ORDER BY name_fr LIMIT %s",
            (f"%{query}%", limit),
        )
        return [_to_food(row) for row in rows]

    async def get(self, ciqual_code: str) -> Food | None:
        rows = await self._repository.execute(
            f"SELECT {_COLUMNS} FROM {SCHEMA}.{TABLE} WHERE ciqual_code = %s",
            (ciqual_code,),
        )
        return _to_food(rows[0]) if rows else None

    async def get_by_name(self, name_search: str) -> Food | None:
        rows = await self._repository.execute(
            f"SELECT {_COLUMNS} FROM {SCHEMA}.{TABLE} WHERE name_search = %s LIMIT 1",
            (name_search,),
        )
        return _to_food(rows[0]) if rows else None

    async def list_all(self, limit: int = 50, offset: int = 0) -> list[Food]:
        rows = await self._repository.execute(
            f"SELECT {_COLUMNS} FROM {SCHEMA}.{TABLE} ORDER BY name_fr LIMIT %s OFFSET %s",
            (limit, offset),
        )
        return [_to_food(row) for row in rows]

    async def upsert_many(self, foods: Iterable[Food]) -> int:
        changed = 0
        for food in foods:
            rows = await self._repository.execute(
                f"""
                INSERT INTO {SCHEMA}.{TABLE} ({_COLUMNS})
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (ciqual_code) DO UPDATE SET
                    name_fr = EXCLUDED.name_fr,
                    name_search = EXCLUDED.name_search,
                    scientific_name = EXCLUDED.scientific_name,
                    group_code = EXCLUDED.group_code,
                    subgroup_code = EXCLUDED.subgroup_code,
                    sub_subgroup_code = EXCLUDED.sub_subgroup_code,
                    group_name = EXCLUDED.group_name,
                    subgroup_name = EXCLUDED.subgroup_name,
                    sub_subgroup_name = EXCLUDED.sub_subgroup_name,
                    kcal_per_100g = EXCLUDED.kcal_per_100g,
                    protein_per_100g = EXCLUDED.protein_per_100g,
                    carb_per_100g = EXCLUDED.carb_per_100g,
                    fat_per_100g = EXCLUDED.fat_per_100g,
                    source = EXCLUDED.source,
                    source_version = EXCLUDED.source_version,
                    updated_at = EXCLUDED.updated_at,
                    nutrition = EXCLUDED.nutrition
                WHERE (
                    {SCHEMA}.{TABLE}.name_fr,
                    {SCHEMA}.{TABLE}.kcal_per_100g,
                    {SCHEMA}.{TABLE}.protein_per_100g,
                    {SCHEMA}.{TABLE}.carb_per_100g,
                    {SCHEMA}.{TABLE}.fat_per_100g,
                    {SCHEMA}.{TABLE}.nutrition
                ) IS DISTINCT FROM (
                    EXCLUDED.name_fr, EXCLUDED.kcal_per_100g, EXCLUDED.protein_per_100g,
                    EXCLUDED.carb_per_100g, EXCLUDED.fat_per_100g, EXCLUDED.nutrition
                )
                RETURNING ciqual_code
                """,
                (
                    food.identity.ciqual_code,
                    food.identity.name,
                    normalize_search(food.identity.name),
                    food.identity.scientific_name,
                    food.classification.group_code,
                    food.classification.subgroup_code,
                    food.classification.sub_subgroup_code,
                    food.classification.group_name,
                    food.classification.subgroup_name,
                    food.classification.sub_subgroup_name,
                    food.nutrition.energy.regulation_1169_kcal,
                    food.nutrition.macronutrients.protein_jones_g,
                    food.nutrition.macronutrients.carbohydrates_g,
                    food.nutrition.macronutrients.fat_g,
                    food.source,
                    food.source_version,
                    food.updated_at,
                    Jsonb(_nutrition_to_json(food.nutrition)),
                ),
            )
            if rows:
                changed += 1
        return changed


def _to_food(row: dict[str, Any]) -> Food:
    return Food(
        identity=FoodIdentity(
            ciqual_code=row["ciqual_code"],
            name=row["name_fr"],
            scientific_name=row["scientific_name"],
        ),
        classification=FoodClassification(
            group_code=row["group_code"],
            subgroup_code=row["subgroup_code"],
            sub_subgroup_code=row["sub_subgroup_code"],
            group_name=row["group_name"],
            subgroup_name=row["subgroup_name"],
            sub_subgroup_name=row["sub_subgroup_name"],
        ),
        nutrition=_nutrition_from_json(row.get("nutrition") or {}),
        source=row["source"],
        source_version=row["source_version"],
        updated_at=row["updated_at"],
    )


def _nutrition_to_json(nutrition: NutritionalComposition) -> dict[str, Any]:
    return {
        "energy": _encode(asdict(nutrition.energy)),
        "macronutrients": _encode(asdict(nutrition.macronutrients)),
        "sugars": _encode(asdict(nutrition.sugars)),
        "fatty_acids": _encode(asdict(nutrition.fatty_acids)),
        "minerals": _encode(asdict(nutrition.minerals)),
        "vitamins": _encode(asdict(nutrition.vitamins)),
    }


def _nutrition_from_json(data: dict[str, Any]) -> NutritionalComposition:
    return NutritionalComposition(
        energy=Energy(**_decode(data.get("energy") or {})),
        macronutrients=Macronutrients(**_decode(data.get("macronutrients") or {})),
        sugars=Sugars(**_decode(data.get("sugars") or {})),
        fatty_acids=FattyAcids(**_decode(data.get("fatty_acids") or {})),
        minerals=Minerals(**_decode(data.get("minerals") or {})),
        vitamins=Vitamins(**_decode(data.get("vitamins") or {})),
    )


def _encode(values: dict[str, Any]) -> dict[str, Any]:
    return {key: str(value) if isinstance(value, Decimal) else value for key, value in values.items()}


def _decode(values: dict[str, Any]) -> dict[str, Any]:
    return {key: Decimal(value) if isinstance(value, str) else value for key, value in values.items()}
