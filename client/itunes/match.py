from client.itunes.parser import get_attributes
from utils.string_utils import get_similarity, is_included


def get_matching_movie(
    candidates: list[dict],
    target_title: str,
    target_directors: list[str],
    target_year: int,
) -> dict:
    best_match = {}
    best_score = 0.0

    for candidate in candidates:
        title, director, year = get_attributes(candidate)

        score = compute_match_score(
            title, director, year, target_title, target_directors, target_year
        )
        if score > best_score:
            best_score = score
            best_match = candidate

    return best_match if best_score > 1.0 else {}


def compute_match_score(
    title: str,
    director: str,
    year: int,
    target_title: str,
    target_directors: list[str],
    target_year: int,
) -> float:
    TITLE_WEIGHT = 1.0
    DIRECTOR_WEIGHT = 0.6
    YEAR_WEIGHT = 0.6

    score = 0.0
    same_title = is_title_match(target_title, title)
    director_score = get_director_score(target_directors, director)
    year_score = get_year_score(target_year, year)

    if same_title:
        score += TITLE_WEIGHT

    if director_score:
        score += director_score * DIRECTOR_WEIGHT

    if year_score:
        score += year_score * YEAR_WEIGHT

    return score


def is_title_match(
    target_title: str,
    title: str,
) -> bool:
    similarity = get_similarity(target_title, title)
    return similarity >= 0.9


def get_director_score(target_directors: list[str], director: str) -> float:
    """
    directors = ["Jason Hand", " Dana Ledoux Miller", "David G. Derrick, Jr."]
    candidate_director = "Jason Hand, Dana Ledoux Miller & David G. Derrick, Jr."
    """
    if not target_directors or director in ("", "Unknown"):
        return 0.0

    for target_director in target_directors:
        if is_included(target_director, director):
            return 1.0

    target_director = "".join(target_directors)
    similarity = get_similarity(target_director, director)
    return -1.0 if similarity < 0.5 else 0.0


def get_year_score(
    target_year: int,
    year: int,
) -> float:
    if target_year <= year <= target_year + 1:
        return 1.0
    if year < target_year - 2 or year > target_year + 2:
        return -1.0
    return 0.0
