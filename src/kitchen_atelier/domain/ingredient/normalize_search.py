import unicodedata


def normalize_search(name: str) -> str:
    folded = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode("ascii")
    return folded.strip().lower()
