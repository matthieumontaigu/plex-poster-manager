import unicodedata
from string import punctuation


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
