import logging

import requests
from requests.models import Response

from client.tmdb.parser import get_country_release_date

logger = logging.getLogger(__name__)


class TMDBAPIRequester:
    def __init__(self, api_token: str) -> None:
        self.api_token = api_token
        self.api_url = "https://api.themoviedb.org/3"
        self.headers = {"accept": "application/json"}
        self.image_base_url = "https://image.tmdb.org/t/p/original"

    def get_movie_title(self, movie_id: int, language: str) -> str | None:
        movie_details = self.get_movie_details(movie_id, language)
        return movie_details.get("title")

    def get_release_date(self, movie_id: int, country_code: str) -> str | None:
        release_dates_info = self.get_release_dates(movie_id)
        results = release_dates_info.get("results", [])
        return get_country_release_date(results, country_code)

    def get_release_dates(self, movie_id: int) -> dict:
        endpoint = f"movie/{movie_id}/release_dates"
        params = {"api_key": self.api_token}
        response = self.get(endpoint, params=params)
        return response.json() if response else {}

    def get_movie_details(self, movie_id: int, language: str) -> dict:
        endpoint = f"movie/{movie_id}"
        params = {"api_key": self.api_token, "language": language}
        response = self.get(endpoint, params=params)
        return response.json() if response else {}

    def get_movie_logo_url(self, movie_id: int, language: str) -> str | None:
        movie_images = self.get_movie_images(movie_id, language)
        logos = movie_images.get("logos", [])
        if logos:
            first_logo = logos[0]
            return f"{self.image_base_url}{first_logo['file_path']}".replace(
                ".svg", ".png"
            )
        return None

    def get_movie_images(self, movie_id: int, language: str) -> dict:
        endpoint = f"movie/{movie_id}/images"
        params = {
            "api_key": self.api_token,
            "language": language,
            "include_image_language": language,
        }
        response = self.get(endpoint, params=params)
        return response.json() if response else {}

    def get(self, endpoint: str, params: dict) -> Response | None:
        url = f"{self.api_url}/{endpoint}"
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            return response
        except requests.exceptions.HTTPError as e:
            logger.error(f"{e}")
            return None
