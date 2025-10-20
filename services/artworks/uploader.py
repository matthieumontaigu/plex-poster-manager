from __future__ import annotations

import logging
import time
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from client.plex.manager import PlexManager
    from models.artworks import Artworks, Image
    from models.movie import Movie


logger = logging.getLogger(__name__)


class ArtworksUploader:
    """Handles uploading artworks to Plex."""

    def __init__(self, plex_manager: PlexManager, upload_interval: float = 1.0):
        self.plex_manager = plex_manager
        self.upload_interval = upload_interval

    def upload(
        self,
        movie: Movie,
        artworks: Artworks,
    ) -> bool:
        uploaded = True

        for artwork_type in ["poster", "background", "logo"]:
            image: Image | None = artworks[artwork_type]
            uploaded &= self.upload_image(movie, artwork_type, image)
            time.sleep(self.upload_interval)

        return uploaded

    def upload_image(
        self, movie: Movie, artwork_type: str, image: Image | None
    ) -> bool:
        if not image:
            return True

        movie_id = movie["plex_movie_id"]
        url = image["url"]

        success = False
        success = self.plex_manager.upload_image(movie_id, artwork_type, url)

        title = movie["title"]
        if success:
            logger.info(
                f"Successfully uploaded {artwork_type} for movie '{title}' (ID: {movie_id})"
            )
        else:
            logger.warning(
                f"Failed to upload {artwork_type} for movie '{title}' (ID: {movie_id}). URL: {url}"
            )

        return success
