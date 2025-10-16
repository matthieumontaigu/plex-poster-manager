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

        for name in ["poster", "background", "logo"]:
            image: Image | None = artworks[name]
            uploaded &= self.upload_image(movie, name, image)
            time.sleep(self.upload_interval)

        return uploaded

    def upload_image(self, movie: Movie, name: str, image: Image | None) -> bool:
        if not image:
            return True

        movie_id = movie["plex_movie_id"]
        url = image["url"]

        success = False
        match name:
            case "poster":
                success = self.plex_manager.upload_poster(movie_id, url)
            case "background":
                success = self.plex_manager.upload_background(movie_id, url)
            case "logo":
                success = self.plex_manager.upload_logo(movie_id, url)
            case _:
                raise ValueError(f"Unknown artwork type: {name}")

        title = movie["title"]
        if success:
            logger.info(
                f"Successfully uploaded {name} for movie '{title}' (ID: {movie_id})"
            )
        else:
            logger.warning(
                f"Failed to upload {name} for movie '{title}' (ID: {movie_id}). URL: {url}"
            )

        return success
