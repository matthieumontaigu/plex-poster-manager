import unicodedata
from string import punctuation


def are_match(s1: str, s2: str) -> bool:
    """
    Check if two strings are equal after normalization.
    """
    return normalize(s1) in normalize(s2)


def normalize(s: str) -> str:
    return remove_punctuation(remove_accents(s)).lower().strip()


def remove_punctuation(s: str) -> str:
    return (
        s.translate(str.maketrans("", "", punctuation))
        .replace("’", "")
        .replace("'", "")
        .replace("`", "")
        .replace(" ", "")
    )


def remove_accents(text: str) -> str:
    normalized = unicodedata.normalize("NFD", text)
    return "".join(c for c in normalized if unicodedata.category(c) != "Mn")
