import requests
from requests import Response


class iTunesAPIRequester:
    BASE_URL = "https://itunes.apple.com"

    def __init__(self):
        pass

    def get_movies(self, country: str, term: str) -> list[dict]:
        params = {"entity": "movie", "country": country, "term": term}
        response = self.get("search", params)
        response_json = response.json()
        if response_json["resultCount"] == 0:
            return []
        return response_json["results"]

    def get(self, endpoint: str, params: dict) -> Response:
        url = f"{self.BASE_URL}/{endpoint}"
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response
