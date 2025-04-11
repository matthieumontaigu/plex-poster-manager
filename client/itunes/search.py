from utils.requests_utils import get_request

BASE_URL = "https://itunes.apple.com"


def search_movies(country: str, term: str) -> list[dict]:
    url = f"{BASE_URL}/search"
    params = {"entity": "movie", "country": country, "term": term}

    response = get_request(url, params=params)
    if response is None:
        return []
    response_json = response.json()
    if response_json["resultCount"] == 0:
        return []
    return response_json["results"]
