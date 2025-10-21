from __future__ import annotations

import logging
import time
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from client.plex.manager import PlexManager
    from services.artworks.updater import ArtworksUpdater
    from storage.movies_cache import MoviesCache

logger = logging.getLogger(__name__)


class RecentlyAddedTask:
    """
    Task that updates artworks for newly added Plex movies.

    Responsibilities:
    - Retrieve newly added Plex movies
    - Use ArtworksUpdater to update their artworks
    - Manage its own cache to avoid reprocessing
    """

    def __init__(
        self,
        plex_manager: PlexManager,
        artworks_updater: ArtworksUpdater,
        recently_added_cache: MoviesCache,
        missing_artworks_cache: MoviesCache,
        sleep_interval: float = 1.0,
    ) -> None:
        self.plex_manager = plex_manager
        self.artworks_updater = artworks_updater
        self.sleep_interval = sleep_interval

        self.recent_cache = recently_added_cache
        self.missing_cache = missing_artworks_cache

    def run(self) -> None:
        logger.info("▶ Updating artworks for recently added movies...")
        self.recent_cache.load()
        self.missing_cache.load()

        recently_added_movies = self.plex_manager.get_recently_added_movies()
        if not recently_added_movies:
            logger.info("No recently added movies found.")
            return

        for movie in recently_added_movies:
            if movie in self.recent_cache:
                continue

            tmdb_id = self.plex_manager.get_tmdb_id(movie["plex_movie_id"])
            if not tmdb_id:
                logger.warning(
                    f"Movie {movie['title']} is not matched in TMDB. Skipping it for now."
                )
                continue

            status, artworks = self.artworks_updater.update(movie, None)

            if status == "upload_failed":
                logger.warning(f"⚠️ Upload failed for {movie['title']}")

            if status == "imperfect_artworks":
                self.recent_cache.add(movie)
                movie_with_artworks = movie.copy()
                movie_with_artworks["artworks"] = artworks
                self.missing_cache.add(movie_with_artworks)
                logger.info(f"⚠️ Incomplete artworks found for {movie['title']}")

            if status == "success":
                self.recent_cache.add(movie)
                logger.info(f"✅ Completed artworks for {movie['title']}")

            time.sleep(self.sleep_interval)

        # Trim cache so only the most recent movies remain relevant
        last_movie = recently_added_movies[-1]
        self.recent_cache.clear(last_movie)

        self.recent_cache.save()
        self.missing_cache.save()

        logger.info("✓ Finished updating artworks for recently added movies")
