import requests
from requests import Response


class PlexAPIRequester:
    def __init__(self, api_url: str, token: str) -> None:
        self.api_url = api_url.rstrip("/")
        self.token = token
        self.headers = {"X-Plex-Token": self.token}

    def get_all_movies(self) -> Response:
        """Get all movies."""
        endpoint = f"library/all"
        params = {"type": 1}

        response = self.get_request(endpoint, params)
        return response

    def get_recently_added_movies(self) -> Response:
        """Get recently added movies."""
        endpoint = f"library/recentlyAdded"
        params = {"type": 1}

        response = self.get_request(endpoint, params)
        return response

    def upload_poster(self, movie_id: int, poster_url: str) -> bool:
        """Upload a poster for a movie."""
        endpoint = f"library/metadata/{movie_id}/posters"
        params = {"url": poster_url}

        response = self.post_request(endpoint, params)
        return response.status_code == 200

    def upload_background(self, movie_id: int, background_url: str) -> bool:
        """Upload a background for a movie."""
        endpoint = f"library/metadata/{movie_id}/arts"
        params = {"url": background_url}

        response = self.post_request(endpoint, params)
        return response.status_code == 200

    def upload_logo(self, movie_id: int, logo_url: str) -> bool:
        """Upload a logo for a movie."""
        endpoint = f"library/metadata/{movie_id}/clearLogos"
        params = {"url": logo_url}

        response = self.post_request(endpoint, params)
        return response.status_code == 200

    def update_release_date(self, movie_id: int, release_date: str) -> bool:
        """Update the release date for a movie."""
        endpoint = f"library/metadata/{movie_id}"
        params = {
            "originallyAvailableAt": release_date,
        }

        response = self.put_request(endpoint, params)
        return response.status_code == 200

    def get_request(self, endpoint: str, params: dict) -> Response:
        url = f"{self.api_url}/{endpoint}"
        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        return response

    def post_request(self, endpoint: str, params: dict) -> Response:
        url = f"{self.api_url}/{endpoint}"
        response = requests.post(url, headers=self.headers, params=params)
        response.raise_for_status()
        return response

    def put_request(self, endpoint: str, params: dict) -> Response:
        url = f"{self.api_url}/{endpoint}"
        response = requests.put(url, headers=self.headers, params=params)
        response.raise_for_status()
        return response
