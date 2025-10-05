from client.itunes.parser import get_kind
from utils.requests_utils import get_request
from utils.string_utils import soft_normalize

BASE_URL = "https://itunes.apple.com"


def search_movies(country: str, term: str) -> list[dict]:
    """
    Search for movies on iTunes.
    Available parameters described here:
    https://performance-partners.apple.com/search-api

    As of 2025-10-06, the "entity" parameter seems to be ignored for movie searches.
    """
    url = f"{BASE_URL}/search"
    term = soft_normalize(term)
    params = {"country": country, "term": term}

    response = get_request(url, params=params)
    if response is None:
        return []
    response_json = response.json()
    if response_json["resultCount"] == 0:
        return []

    # Filter out non-movie results
    results = [
        result
        for result in response_json["results"]
        if get_kind(result) == "feature-movie"
    ]
    return results
