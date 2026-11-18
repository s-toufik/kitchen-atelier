class RecipeNotFound(Exception):
    def __init__(self, recipe_id: str) -> None:
        super().__init__(f"recipe {recipe_id!r} not found")
        self.recipe_id = recipe_id
