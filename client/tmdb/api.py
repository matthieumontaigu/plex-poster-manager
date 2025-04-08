import requests
from requests.models import Response


class TMDBAPIRequester:
    def __init__(self, api_token: str) -> None:
        self.api_token = api_token
        self.api_url = "https://api.themoviedb.org/3"

    def get_movie_title(self, movie_id: int, language: str) -> str:
        movie_details = self.get_movie_details(movie_id, language)
        return movie_details["title"]

    def get_movie_details(self, movie_id: int, language: str) -> dict:
        endpoint = f"movie/{movie_id}"
        params = {"api_key": self.api_token, "language": language}
        response = self.get(endpoint, params=params)
        return response.json()

    def get(self, endpoint: str, params: dict) -> Response:
        url = f"{self.api_url}/{endpoint}"
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response
