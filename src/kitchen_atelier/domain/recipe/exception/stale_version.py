class StaleVersion(Exception):
    def __init__(self, recipe_id: str, expected_version_number: int, latest_version_number: int) -> None:
        super().__init__(
            f"recipe {recipe_id!r}: draft was based on version {expected_version_number} "
            f"but the latest saved version is {latest_version_number}"
        )
        self.recipe_id = recipe_id
        self.expected_version_number = expected_version_number
        self.latest_version_number = latest_version_number
