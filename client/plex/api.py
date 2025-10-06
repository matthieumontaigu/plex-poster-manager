import logging

import requests
from requests import Response

logger = logging.getLogger(__name__)


class PlexAPIRequester:
    def __init__(self, api_url: str, plex_token: str) -> None:
        self.api_url = api_url.rstrip("/")
        self.headers = {
            "X-Plex-Token": plex_token,
            "X-Plex-Product": "Plex poster manager",
            "X-Plex-Pms-Api-Version": "1.0",
        }

    def get_all_movies(self) -> Response | None:
        """Get all movies."""
        endpoint = f"library/sections/6/all"

        response = self.get(endpoint, {})
        return response

    def get_recently_added_movies(self) -> Response | None:
        """Get recently added movies."""
        endpoint = f"library/sections/6/recentlyAdded"
        params = {"type": 1}

        response = self.get(endpoint, params)
        return response

    def get_metadata(self, movie_id: int) -> Response | None:
        """Get metadata for a specific movie."""
        endpoint = f"library/metadata/{movie_id}"

        response = self.get(endpoint, {})
        return response

    def get_logos(self, movie_id: int) -> Response | None:
        """Get logos for a specific movie."""
        endpoint = f"library/metadata/{movie_id}/clearLogos"

        response = self.get(endpoint, {})
        return response

    def upload_poster(self, movie_id: int, poster_url: str) -> bool:
        """Upload a poster for a movie."""
        endpoint = f"library/metadata/{movie_id}/posters"
        params = {"url": poster_url}

        response = self.post(endpoint, params)
        if response is None:
            return False
        return response.status_code == 200

    def upload_background(self, movie_id: int, background_url: str) -> bool:
        """Upload a background for a movie."""
        endpoint = f"library/metadata/{movie_id}/arts"
        params = {"url": background_url}

        response = self.post(endpoint, params)
        if response is None:
            return False
        return response.status_code == 200

    def upload_logo(self, movie_id: int, logo_url: str) -> bool:
        """Upload a logo for a movie."""
        endpoint = f"library/metadata/{movie_id}/clearLogos"
        params = {"url": logo_url}

        response = self.post(endpoint, params)
        if response is None:
            return False
        return response.status_code == 200

    def upload_logo_file(self, movie_id: int, logo_file_path: str) -> bool:
        """Upload a logo for a movie."""
        endpoint = f"library/metadata/{movie_id}/clearLogos"
        with open(logo_file_path, "rb") as f:
            logo_data = f.read()

        response = self.post(endpoint, data=logo_data)
        if response is None:
            return False
        return response.status_code == 200

    def update_release_date(self, movie_id: int, release_date: str) -> bool:
        """Update the release date for a movie."""
        endpoint = f"library/metadata/{movie_id}"
        params = {
            "originallyAvailableAt": release_date,
        }

        response = self.put(endpoint, params)
        if response is None:
            return False
        return response.status_code == 200

    def get(self, endpoint: str, params: dict) -> Response | None:
        url = f"{self.api_url}/{endpoint}"
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            return response
        except requests.exceptions.HTTPError as e:
            logger.error(f"{e}")
            return None

    def post(
        self, endpoint: str, params: dict | None = None, **kwargs
    ) -> Response | None:
        url = f"{self.api_url}/{endpoint}"
        try:
            response = requests.post(url, headers=self.headers, params=params, **kwargs)
            response.raise_for_status()
            return response
        except requests.exceptions.HTTPError as e:
            logger.error(f"{e}")
            return None

    def put(self, endpoint: str, params: dict) -> Response | None:
        url = f"{self.api_url}/{endpoint}"
        try:
            response = requests.put(url, headers=self.headers, params=params)
            response.raise_for_status()
            return response
        except requests.exceptions.HTTPError as e:
            logger.error(f"{e}")
            return None
