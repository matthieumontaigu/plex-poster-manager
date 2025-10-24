from __future__ import annotations

import logging
import time
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from client.plex.manager import PlexManager
    from services.artworks.updater import ArtworksUpdater
    from storage.movies_cache import MoviesCache

logger = logging.getLogger(__name__)


class MissingArtworksTask:
    """
    Task that retries updating artworks for movies with missing or incomplete artworks.

    Responsibilities:
    - Iterate over cached "missing artworks" movies
    - Retry artwork update using ArtworksUpdater
    - Remove from cache once complete
    """

    def __init__(
        self,
        plex_manager: PlexManager,
        artworks_updater: ArtworksUpdater,
        missing_artworks_cache: MoviesCache,
        sleep_interval: float = 1.0,
    ) -> None:
        self.plex_manager = plex_manager
        self.artworks_updater = artworks_updater
        self.sleep_interval = sleep_interval

        self.cache = missing_artworks_cache

    def run(self) -> None:
        self.cache.load()

        to_remove = []

        for plex_movie_id, movie in self.cache.items():
            if not self.plex_manager.exists(plex_movie_id):
                to_remove.append(movie)
                continue

            # Movie will have its TMDB ID already set in the cache
            current_artworks = movie.get("artworks")
            status, new_artworks = self.artworks_updater.update(movie, current_artworks)

            if status == "success":
                logger.info(f"✓ Complete artworks found for {movie['title']}")
                to_remove.append(movie)

            elif status == "upload_failed":
                logger.warning(f"✗ Upload failed for {movie['title']}")

            elif status == "unchanged_artworks":
                logger.info(f"⚠ No changes for {movie['title']}")

            elif status == "imperfect_artworks":
                movie["artworks"] = new_artworks
                logger.info(f"⚠ Incomplete artworks remain for {movie['title']}")

            time.sleep(self.sleep_interval)

        self.cache.remove_all(to_remove)
        self.cache.save()
