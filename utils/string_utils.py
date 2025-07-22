import unicodedata
from difflib import SequenceMatcher
from string import punctuation


def are_match(s1: str, s2: str) -> bool:
    """
    Check if two strings are equal after normalization.
    """
    return normalize(s1) == normalize(s2)


def is_included(s1: str, s2: str) -> bool:
    """
    Check if s1 is included in s2 after normalization.
    """
    return normalize(s1) in normalize(s2)


def get_similarity(s1: str, s2: str) -> float:
    return SequenceMatcher(None, normalize(s1), normalize(s2)).ratio()


def normalize(s: str) -> str:
    return remove_punctuation(remove_accents(s)).lower().strip()


def soft_normalize(s: str) -> str:
    return remove_special_characters(s.lower())


def remove_punctuation(s: str) -> str:
    return (
        s.translate(str.maketrans("", "", punctuation))
        .replace("’", "")
        .replace("'", "")
        .replace("`", "")
        .replace(" ", "")
    )


def remove_special_characters(s: str) -> str:
    return s.replace("*", "").replace("&", "")


def remove_accents(text: str) -> str:
    normalized = unicodedata.normalize("NFD", text)
    return "".join(c for c in normalized if unicodedata.category(c) != "Mn")
