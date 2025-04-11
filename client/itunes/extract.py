from client.itunes.match import get_matching_movie
from client.itunes.parser import get_artworks
from client.itunes.search import search_movies


def get_itunes_artworks(
    title: str, directors: list[str], year: int, country: str
) -> tuple[str, str, str] | None:
    candidates = search_movies(country, title.lower())
    if not candidates:
        return None

    match = get_matching_movie(candidates, title, directors, year)
    if not match:
        return None

    itunes_url, poster_url, release_date = get_artworks(match)
    return itunes_url, poster_url, release_date
