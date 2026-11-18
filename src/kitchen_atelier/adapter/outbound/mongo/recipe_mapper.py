from datetime import UTC
from typing import Any

from kitchen_atelier.domain.recipe.ingredient_line import IngredientLine
from kitchen_atelier.domain.recipe.recipe import Recipe
from kitchen_atelier.domain.recipe.recipe_draft import RecipeDraft, Sensory, Step
from kitchen_atelier.domain.recipe.recipe_version import RecipeVersion
from kitchen_atelier.domain.recipe.unit import Unit


def recipe_to_document(recipe: Recipe) -> dict[str, Any]:
    return {
        "_id": recipe.id,
        "title": recipe.title,
        "course": recipe.course,
        "current_version_number": recipe.current_version_number,
        "created_at": recipe.created_at,
        "updated_at": recipe.updated_at,
    }


def recipe_from_document(document: dict[str, Any]) -> Recipe:
    return Recipe(
        id=document["_id"],
        title=document["title"],
        course=document["course"],
        current_version_number=document["current_version_number"],
        created_at=_aware(document["created_at"]),
        updated_at=_aware(document["updated_at"]),
    )


def version_to_document(version: RecipeVersion) -> dict[str, Any]:
    draft = version.draft
    return {
        "recipe_id": version.recipe_id,
        "version_number": version.version_number,
        "saved_at": version.saved_at,
        "title": draft.title,
        "subtitle": draft.subtitle,
        "course": draft.course,
        "portions": draft.portions,
        "prep_time_minutes": draft.prep_time_minutes,
        "cook_time_minutes": draft.cook_time_minutes,
        "ingredients": [_line_to_document(line) for line in draft.ingredients],
        "steps": [{"text": step.text, "tags": list(step.tags)} for step in draft.steps],
        "sensory": {
            "seasoning": draft.sensory.seasoning,
            "acidity": draft.sensory.acidity,
            "texture": draft.sensory.texture,
        },
        "notes": draft.notes,
    }


def version_from_document(document: dict[str, Any]) -> RecipeVersion:
    draft = RecipeDraft(
        title=document["title"],
        subtitle=document["subtitle"],
        course=document["course"],
        portions=document["portions"],
        prep_time_minutes=document["prep_time_minutes"],
        cook_time_minutes=document["cook_time_minutes"],
        ingredients=tuple(_line_from_document(line) for line in document["ingredients"]),
        steps=tuple(Step(text=step["text"], tags=tuple(step["tags"])) for step in document["steps"]),
        sensory=Sensory(**document["sensory"]),
        notes=document.get("notes", ""),
    )
    return RecipeVersion(
        recipe_id=document["recipe_id"],
        version_number=document["version_number"],
        saved_at=_aware(document["saved_at"]),
        draft=draft,
    )


def _line_to_document(line: IngredientLine) -> dict[str, Any]:
    return {
        "name": line.name,
        "quantity": line.quantity,
        "unit": line.unit.value,
        "kcal_per_100g": line.kcal_per_100g,
        "protein_per_100g": line.protein_per_100g,
        "carb_per_100g": line.carb_per_100g,
        "fat_per_100g": line.fat_per_100g,
        "ingredient_ref_id": line.ingredient_ref_id,
    }


def _line_from_document(document: dict[str, Any]) -> IngredientLine:
    return IngredientLine(
        name=document["name"],
        quantity=document["quantity"],
        unit=Unit(document["unit"]),
        kcal_per_100g=document["kcal_per_100g"],
        protein_per_100g=document["protein_per_100g"],
        carb_per_100g=document["carb_per_100g"],
        fat_per_100g=document["fat_per_100g"],
        ingredient_ref_id=document.get("ingredient_ref_id"),
    )


def _aware(value: Any) -> Any:
    return value.replace(tzinfo=UTC) if value.tzinfo is None else value
