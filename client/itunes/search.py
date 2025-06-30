from utils.requests_utils import get_request
from utils.string_utils import soft_normalize

BASE_URL = "https://itunes.apple.com"


def search_movies(country: str, term: str) -> list[dict]:
    url = f"{BASE_URL}/search"
    term = soft_normalize(term)
    params = {"entity": "movie", "country": country, "term": term}

    response = get_request(url, params=params)
    if response is None:
        return []
    response_json = response.json()
    if response_json["resultCount"] == 0:
        return []
    return response_json["results"]
