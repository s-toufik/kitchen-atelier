class IngredientNotFound(Exception):
    def __init__(self, ciqual_code: str) -> None:
        super().__init__(f"ingredient {ciqual_code!r} not found")
        self.ciqual_code = ciqual_code
