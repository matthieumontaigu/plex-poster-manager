from __future__ import annotations

import logging
import time
from typing import TYPE_CHECKING

from client.plex.image import get_last_upload_if_agent_selected

if TYPE_CHECKING:
    from client.plex.image import PlexImage
    from client.plex.manager import PlexManager
    from models.movie import Movie

logger = logging.getLogger(__name__)


class ArtworksReverter:

    def __init__(
        self,
        plex_manager: PlexManager,
        artworks_types: list[str],
    ) -> None:
        if set(artworks_types).difference({"poster", "background", "logo"}):
            raise ValueError(
                "artworks_types should be a subset of poster, background, logo"
            )
        self.plex_manager = plex_manager
        self.artworks_types = artworks_types
        self.sleep_interval = 0.1  # seconds

    def process_all_movies(self) -> None:
        movies = self.plex_manager.get_all_movies()
        movies_sorted = sorted(
            movies, key=lambda movie: movie["added_date"], reverse=True
        )
        self.process_artworks(movies_sorted)

    def process_artworks(self, movies: list[Movie]) -> None:
        for artwork_type in self.artworks_types:
            logger.info(f"Processing artwork type: {artwork_type}")
            self.process_artwork_type(movies, artwork_type)

    def process_artwork_type(self, movies: list[Movie], artwork_type: str) -> None:
        for movie in movies:
            self.process_image(movie, artwork_type)
            time.sleep(self.sleep_interval)

    def process_image(self, movie: Movie, artwork_type: str) -> None:
        plex_movie_id = movie["plex_movie_id"]
        images = self.plex_manager.get_images(plex_movie_id, artwork_type)
        last_uploaded = get_last_upload_if_agent_selected(images)
        if last_uploaded is None:
            return None

        logger.info(
            f"Will revert {artwork_type} for {movie['title']} ({movie['plex_movie_id']})"
        )
        success = self.revert(plex_movie_id, artwork_type, last_uploaded)
        if success:
            logger.info(
                f"Reverted {artwork_type} for {movie['title']} ({movie['plex_movie_id']})"
            )
        else:
            logger.error(
                f"Failed to revert {artwork_type} for {movie['title']} ({movie['plex_movie_id']})"
            )

    def revert(self, plex_movie_id: int, artwork_type: str, image: PlexImage) -> bool:
        image_path = self.plex_manager.get_movie_image_path(image["key"])
        logger.info(f"Will upload {image_path}.")

        success = self.plex_manager.upload_image_file(
            plex_movie_id, artwork_type, image_path
        )
        return success
