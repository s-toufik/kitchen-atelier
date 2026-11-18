from pydantic import BaseModel, Field

from kitchen_atelier.domain.recipe.ingredient_line import IngredientLine
from kitchen_atelier.domain.recipe.recipe_draft import RecipeDraft, Sensory, Step
from kitchen_atelier.domain.recipe.unit import Unit


class IngredientLineSchema(BaseModel):
    name: str = Field(min_length=1)
    quantity: float = Field(ge=0)
    unit: Unit
    kcal_per_100g: float = Field(ge=0)
    protein_per_100g: float = Field(ge=0)
    carb_per_100g: float = Field(ge=0)
    fat_per_100g: float = Field(ge=0)
    ingredient_ref_id: str | None = None

    def to_domain(self) -> IngredientLine:
        return IngredientLine(
            name=self.name,
            quantity=self.quantity,
            unit=self.unit,
            kcal_per_100g=self.kcal_per_100g,
            protein_per_100g=self.protein_per_100g,
            carb_per_100g=self.carb_per_100g,
            fat_per_100g=self.fat_per_100g,
            ingredient_ref_id=self.ingredient_ref_id,
        )

    @classmethod
    def from_domain(cls, line: IngredientLine) -> IngredientLineSchema:
        return cls(
            name=line.name,
            quantity=line.quantity,
            unit=line.unit,
            kcal_per_100g=line.kcal_per_100g,
            protein_per_100g=line.protein_per_100g,
            carb_per_100g=line.carb_per_100g,
            fat_per_100g=line.fat_per_100g,
            ingredient_ref_id=line.ingredient_ref_id,
        )


class StepSchema(BaseModel):
    text: str = Field(min_length=1)
    tags: list[str] = Field(default_factory=list)

    def to_domain(self) -> Step:
        return Step(text=self.text, tags=tuple(self.tags))

    @classmethod
    def from_domain(cls, step: Step) -> StepSchema:
        return cls(text=step.text, tags=list(step.tags))


class SensorySchema(BaseModel):
    seasoning: str = "Balanced"
    acidity: str = "Balanced"
    texture: str = "Spot-On"

    def to_domain(self) -> Sensory:
        return Sensory(seasoning=self.seasoning, acidity=self.acidity, texture=self.texture)

    @classmethod
    def from_domain(cls, sensory: Sensory) -> SensorySchema:
        return cls(seasoning=sensory.seasoning, acidity=sensory.acidity, texture=sensory.texture)


class RecipeDraftSchema(BaseModel):
    title: str = Field(min_length=1)
    subtitle: str = ""
    course: str
    portions: int = Field(ge=1)
    prep_time_minutes: int = Field(ge=0)
    cook_time_minutes: int = Field(ge=0)
    ingredients: list[IngredientLineSchema] = Field(min_length=1)
    steps: list[StepSchema] = Field(min_length=1)
    sensory: SensorySchema = Field(default_factory=SensorySchema)
    notes: str = ""

    def to_domain(self) -> RecipeDraft:
        return RecipeDraft(
            title=self.title,
            subtitle=self.subtitle,
            course=self.course,
            portions=self.portions,
            prep_time_minutes=self.prep_time_minutes,
            cook_time_minutes=self.cook_time_minutes,
            ingredients=tuple(line.to_domain() for line in self.ingredients),
            steps=tuple(step.to_domain() for step in self.steps),
            sensory=self.sensory.to_domain(),
            notes=self.notes,
        )

    @classmethod
    def from_domain(cls, draft: RecipeDraft) -> RecipeDraftSchema:
        return cls(
            title=draft.title,
            subtitle=draft.subtitle,
            course=draft.course,
            portions=draft.portions,
            prep_time_minutes=draft.prep_time_minutes,
            cook_time_minutes=draft.cook_time_minutes,
            ingredients=[IngredientLineSchema.from_domain(line) for line in draft.ingredients],
            steps=[StepSchema.from_domain(step) for step in draft.steps],
            sensory=SensorySchema.from_domain(draft.sensory),
            notes=draft.notes,
        )
