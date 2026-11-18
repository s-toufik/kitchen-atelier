from collections.abc import Iterable

from pycraftcore.repository.port import AsyncRepository

from kitchen_atelier.domain.ingredient.ingredient import Ingredient

SCHEMA: str = "kitchen"
TABLE: str = "ingredients"
_COLUMNS: str = (
    "ciqual_code, name_fr, name_search, kcal_per_100g, protein_per_100g, "
    "carb_per_100g, fat_per_100g, source, updated_at"
)


class SqlIngredientRepository:
    def __init__(self, repository: AsyncRepository) -> None:
        self._repository = repository

    async def search(self, query: str, limit: int = 20) -> list[Ingredient]:
        rows = await self._repository.execute(
            f"SELECT {_COLUMNS} FROM {SCHEMA}.{TABLE} "
            "WHERE name_search LIKE %s ORDER BY name_fr LIMIT %s",
            (f"%{query}%", limit),
        )
        return [_to_ingredient(row) for row in rows]

    async def get(self, ciqual_code: str) -> Ingredient | None:
        rows = await self._repository.execute(
            f"SELECT {_COLUMNS} FROM {SCHEMA}.{TABLE} WHERE ciqual_code = %s",
            (ciqual_code,),
        )
        return _to_ingredient(rows[0]) if rows else None

    async def upsert_many(self, ingredients: Iterable[Ingredient]) -> int:
        changed = 0
        for ingredient in ingredients:
            rows = await self._repository.execute(
                f"""
                INSERT INTO {SCHEMA}.{TABLE} ({_COLUMNS})
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (ciqual_code) DO UPDATE SET
                    name_fr = EXCLUDED.name_fr,
                    name_search = EXCLUDED.name_search,
                    kcal_per_100g = EXCLUDED.kcal_per_100g,
                    protein_per_100g = EXCLUDED.protein_per_100g,
                    carb_per_100g = EXCLUDED.carb_per_100g,
                    fat_per_100g = EXCLUDED.fat_per_100g,
                    source = EXCLUDED.source,
                    updated_at = EXCLUDED.updated_at
                WHERE (
                    {SCHEMA}.{TABLE}.name_fr,
                    {SCHEMA}.{TABLE}.kcal_per_100g,
                    {SCHEMA}.{TABLE}.protein_per_100g,
                    {SCHEMA}.{TABLE}.carb_per_100g,
                    {SCHEMA}.{TABLE}.fat_per_100g
                ) IS DISTINCT FROM (
                    EXCLUDED.name_fr, EXCLUDED.kcal_per_100g, EXCLUDED.protein_per_100g,
                    EXCLUDED.carb_per_100g, EXCLUDED.fat_per_100g
                )
                RETURNING ciqual_code
                """,
                (
                    ingredient.ciqual_code,
                    ingredient.name_fr,
                    ingredient.name_search,
                    ingredient.kcal_per_100g,
                    ingredient.protein_per_100g,
                    ingredient.carb_per_100g,
                    ingredient.fat_per_100g,
                    ingredient.source,
                    ingredient.updated_at,
                ),
            )
            if rows:
                changed += 1
        return changed


def _to_ingredient(row: dict) -> Ingredient:
    return Ingredient(
        ciqual_code=row["ciqual_code"],
        name_fr=row["name_fr"],
        name_search=row["name_search"],
        kcal_per_100g=row["kcal_per_100g"],
        protein_per_100g=row["protein_per_100g"],
        carb_per_100g=row["carb_per_100g"],
        fat_per_100g=row["fat_per_100g"],
        source=row["source"],
        updated_at=row["updated_at"],
    )
