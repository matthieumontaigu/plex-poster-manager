import logging

from client.plex.api import PlexAPIRequester
from client.plex.parser import get_movie_attributes, get_movies


class PlexManager:
    def __init__(self, plex_url: str, plex_token: str) -> None:
        self.api_requester = PlexAPIRequester(plex_url, plex_token)
        self.logger = logging.getLogger(__name__)

    def get_all_movies(self) -> list[dict[str, str | int | None]]:
        api_response = self.api_requester.get_all_movies()
        if api_response is None:
            self.logger.error("Failed to fetch all movies from Plex.")
            return []
        return get_movies(api_response)

    def get_recently_added_movies(self) -> list[dict[str, str | int | None]]:
        api_response = self.api_requester.get_recently_added_movies()
        if api_response is None:
            self.logger.error("Failed to fetch recently added movies from Plex.")
            return []
        return get_movies(api_response)

    def upload_poster(self, plex_movie_id: int, poster_url: str) -> bool:
        return self.api_requester.upload_poster(plex_movie_id, poster_url)

    def upload_background(self, movie_id: int, background_url: str) -> bool:
        return self.api_requester.upload_background(movie_id, background_url)

    def upload_logo(self, movie_id: int, logo_url: str) -> bool:
        return self.api_requester.upload_logo(movie_id, logo_url)

    def update_release_date(self, movie_id: int, release_date: str) -> bool:
        return self.api_requester.update_release_date(movie_id, release_date)

    def exists(self, movie_id: int) -> bool:
        """
        Check if a movie exists in the Plex library by its ID.
        :param movie_id: The Plex movie ID.
        :return: True if the movie exists, False otherwise.
        """
        api_response = self.api_requester.get_metadata(movie_id)
        return api_response is not None

    def get_metadata(self, movie_id: int) -> dict[str, str | None]:
        api_response = self.api_requester.get_metadata(movie_id)
        if api_response is None:
            return {}
        return get_movie_attributes(api_response)

    def get_tmdb_id(self, movie_id: int) -> str | None:
        metadata = self.get_metadata(movie_id)
        return metadata.get("tmdb_id")
