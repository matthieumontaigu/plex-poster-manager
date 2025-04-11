from client.itunes.parser import get_director, get_title, get_year
from utils.string_utils import are_match


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
    TITLE_SCORE = 1.0
    DIRECTOR_SCORE = 0.6
    YEAR_SCORE = 0.6

    score = 0.0
    same_title = are_match(title, get_title(candidate))
    same_director = is_director_match(directors, get_director(candidate))
    same_year = is_year_match(year, get_year(candidate))

    if same_title:
        score += TITLE_SCORE

    if same_director:
        score += DIRECTOR_SCORE

    if same_year:
        score += YEAR_SCORE

    return score


def is_director_match(directors: list[str], candidate_director: str) -> bool:
    """
    directors = ["Jason Hand", " Dana Ledoux Miller", "David G. Derrick, Jr."]
    candidate_director = "Jason Hand, Dana Ledoux Miller & David G. Derrick, Jr."
    """
    if not directors:
        return True

    for director in directors:
        if are_match(director, candidate_director):
            return True

    return False


def is_year_match(
    year: int,
    candidate_year: int,
) -> bool:
    return year <= candidate_year <= year + 1
