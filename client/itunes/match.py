from client.itunes.parser import get_director, get_title, get_year
from utils.string_utils import get_similarity, is_included


def get_matching_movie(
    candidates: list[dict], title: str, directors: list[str], year: int
) -> dict:
    best_match = {}
    best_score = 0.0

    for candidate in candidates:
        score = compute_match_score(candidate, title, directors, year)
        if score > best_score:
            best_score = score
            best_match = candidate

    return best_match if best_score > 1.0 else {}


def compute_match_score(
    candidate: dict, title: str, directors: list[str], year: int
) -> float:
    TITLE_WEIGHT = 1.0
    DIRECTOR_WEIGHT = 0.6
    YEAR_WEIGHT = 0.6

    score = 0.0
    same_title = is_title_match(title, get_title(candidate))
    director_score = get_director_score(directors, get_director(candidate))
    same_year = is_year_match(year, get_year(candidate))

    if same_title:
        score += TITLE_WEIGHT

    if director_score:
        score += director_score * DIRECTOR_WEIGHT

    if same_year:
        score += YEAR_WEIGHT

    return score


def is_title_match(
    title: str,
    candidate_title: str,
) -> bool:
    similarity = get_similarity(title, candidate_title)
    return similarity >= 0.9


def get_director_score(directors: list[str], candidate_director: str) -> float:
    """
    directors = ["Jason Hand", " Dana Ledoux Miller", "David G. Derrick, Jr."]
    candidate_director = "Jason Hand, Dana Ledoux Miller & David G. Derrick, Jr."
    """
    if not directors or candidate_director in ("", "Unknown"):
        return 0.0

    for director in directors:
        if is_included(director, candidate_director):
            return 1.0

    director = "".join(directors)
    similarity = get_similarity(director, candidate_director)
    return -1.0 if similarity < 0.5 else 0.0


def is_year_match(
    year: int,
    candidate_year: int,
) -> bool:
    return year <= candidate_year <= year + 1
