from __future__ import annotations

import hashlib
import logging
from typing import TYPE_CHECKING

from client.plex.api import PlexAPIRequester
from client.plex.parser import parse_movie, parse_movies, parse_photos

if TYPE_CHECKING:
    from models.movie import Movie

logger = logging.getLogger(__name__)


class PlexManager:
    def __init__(
        self,
        plex_url: str,
        plex_token: str,
        metadata_country: str,
        metadata_path: str = "",
    ) -> None:
        self.api_requester = PlexAPIRequester(plex_url, plex_token)
        self.country = metadata_country
        self.metadata_path = metadata_path

    def get_all_movies(self) -> list[Movie]:
        api_response = self.api_requester.get_all_movies()
        if api_response is None:
            logger.error("Failed to fetch all movies from Plex.")
            return []
        return parse_movies(api_response, self.country)

    def get_recently_added_movies(self) -> list[Movie]:
        api_response = self.api_requester.get_recently_added_movies()
        if api_response is None:
            logger.error("Failed to fetch recently added movies from Plex.")
            return []
        return parse_movies(api_response, self.country)

    def upload_poster(self, plex_movie_id: int, poster_url: str) -> bool:
        return self.api_requester.upload_poster(plex_movie_id, poster_url)

    def upload_background(self, movie_id: int, background_url: str) -> bool:
        return self.api_requester.upload_background(movie_id, background_url)

    def upload_logo(self, movie_id: int, logo_url: str) -> bool:
        return self.api_requester.upload_logo(movie_id, logo_url)

    def upload_logo_file(self, movie_id: int, logo_file_path: str) -> bool:
        return self.api_requester.upload_logo_file(movie_id, logo_file_path)

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

    def get_metadata(self, movie_id: int) -> Movie | None:
        api_response = self.api_requester.get_metadata(movie_id)
        if api_response is None:
            return None
        return parse_movie(api_response, self.country)

    def get_tmdb_id(self, movie_id: int) -> int | None:
        metadata = self.get_metadata(movie_id)
        return metadata["tmdb_id"] if metadata else None

    def get_plex_guid(self, movie_id: int) -> str | None:
        metadata = self.get_metadata(movie_id)
        return metadata["guid"] if metadata else None

    def get_bundle_id(self, movie_id: int) -> str | None:
        plex_guid = self.get_plex_guid(movie_id)
        if not plex_guid:
            return None
        bundle_hash = hashlib.sha1(plex_guid.encode("utf-8")).hexdigest()
        return bundle_hash

    def get_movie_bundle_path(self, movie_id: int) -> str:
        bundle_id = self.get_bundle_id(movie_id)
        if not bundle_id:
            return ""
        subfolder = bundle_id[0]
        bundle_folder = bundle_id[1:]
        return f"{self.metadata_path}/Movies/{subfolder}/{bundle_folder}.bundle"

    def get_logos(self, movie_id: int) -> list[dict[str, str]]:
        api_response = self.api_requester.get_logos(movie_id)
        if api_response is None:
            return []
        return parse_photos(api_response)

    def get_movie_image_path(self, key: str) -> str:
        """
        Get the full path to an image based on its key.
        :param key: The key of the image.
        /library/metadata/55579/file?url=metadata://clearLogos/tv.plex.agents.movie_496540d6360cbcdd5aaa8f073958ab2627fad632
        /library/metadata/55579/file?url=upload://clearLogos/05dc99b9805c5fa3a8915b5421879394a94b0904
        :return: The full path to the image.
        """
        movie_id = int(key.split("/")[3])
        bundle_path = self.get_movie_bundle_path(movie_id)

        url = key.split("url=")[-1]
        if url.startswith("metadata://"):
            middle_path = "Contents/_combined"
        elif url.startswith("upload://"):
            middle_path = "Uploads"
        else:
            return ""

        image_path = url.split("://")[-1]
        return f"{bundle_path}/{middle_path}/{image_path}"
