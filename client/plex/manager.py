import logging
import time

from client.plex.parser import get_movie_attributes, get_movies

from .api import PlexAPIRequester


class PlexManager:
    def __init__(self, plex_url: str, plex_token: str) -> None:
        self.api_requester = PlexAPIRequester(plex_url, plex_token)
        self.logger = logging.getLogger(__name__)

    def get_all_movies(self) -> list[dict[str, str | None]]:
        api_response = self.api_requester.get_all_movies()
        return get_movies(api_response)

    def get_recently_added_movies(self) -> list[dict[str, str | None]]:
        api_response = self.api_requester.get_recently_added_movies()
        return get_movies(api_response)

    def update_artworks(
        self, plex_movie_id: int, poster_url: str, background_url: str, logo_url: str
    ) -> bool:
        """
        Update the movie artworks (poster, background, logo) for a given Plex movie ID.
        :param plex_movie_id: The Plex movie ID.
        :param poster_url: The URL of the poster image.
        :param background_url: The URL of the background image.
        :param logo_url: The URL of the logo image.
        :return: True if all uploads were successful, False otherwise.
        """
        success = True
        if poster_url:
            success &= self.upload_poster(plex_movie_id, poster_url)
            time.sleep(0.5)
        if background_url:
            success &= self.upload_background(plex_movie_id, background_url)
            time.sleep(0.5)
        if logo_url:
            success &= self.upload_logo(plex_movie_id, logo_url)
            time.sleep(0.5)
        return success

    def upload_poster(self, plex_movie_id: int, poster_url: str) -> bool:
        return self.api_requester.upload_poster(plex_movie_id, poster_url)

    def upload_background(self, movie_id: int, background_url: str) -> bool:
        return self.api_requester.upload_background(movie_id, background_url)

    def upload_logo(self, movie_id: int, logo_url: str) -> bool:
        return self.api_requester.upload_logo(movie_id, logo_url)

    def update_release_date(self, movie_id: int, release_date: str) -> bool:
        return self.api_requester.update_release_date(movie_id, release_date)

    def get_metadata(self, movie_id: int) -> dict[str, str | None]:
        api_response = self.api_requester.get_metadata(movie_id)
        return get_movie_attributes(api_response)

    def get_tmdb_id(self, movie_id: int) -> str | None:
        metadata = self.get_metadata(movie_id)
        return metadata.get("tmdb_id")
