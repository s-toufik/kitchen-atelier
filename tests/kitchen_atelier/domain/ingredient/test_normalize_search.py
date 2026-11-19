from kitchen_atelier.domain.ingredient.normalize_search import normalize_search


def test_normalize_search_strips_accents_and_case() -> None:
    assert normalize_search("Crème fraîche") == "creme fraiche"
