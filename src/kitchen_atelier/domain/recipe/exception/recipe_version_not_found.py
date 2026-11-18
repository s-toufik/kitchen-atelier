class RecipeVersionNotFound(Exception):
    def __init__(self, recipe_id: str, version_number: int) -> None:
        super().__init__(f"recipe {recipe_id!r} has no version {version_number}")
        self.recipe_id = recipe_id
        self.version_number = version_number
