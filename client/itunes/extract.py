from datetime import datetime

from client.itunes.parser import get_artworks, get_director, get_title, get_year
from client.itunes.search import search_movies
from utils.string_utils import are_match


def get_itunes_artworks(
    title: str, directors: list[str], year: int, country: str
) -> tuple[str, str, str] | None:
    candidates = search_movies(country, title.lower())

    match = get_matching_movie(candidates, title, directors, year)
    if not match:
        return None

    itunes_url, poster_url, release_date = get_artworks(match)
    return itunes_url, poster_url, release_date


def get_matching_movie(
    candidates: list[dict], title: str, directors: list[str], year: int
) -> dict:
    for candidate in candidates:
        if is_matching(candidate, title, directors, year):
            return candidate
    return {}


def is_matching(candidate: dict, title: str, directors: list[str], year: int) -> bool:
    same_title = are_match(title, get_title(candidate))
    if not same_title:
        return False

    same_director = is_director_match(directors, get_director(candidate))
    same_year = is_year_match(year, get_year(candidate))
    return same_director or same_year


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
