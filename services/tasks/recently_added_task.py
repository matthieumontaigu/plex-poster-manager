from __future__ import annotations

import logging
import time
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from client.plex.manager import PlexManager
    from models.movie import Movie
    from services.artworks.updater import ArtworksUpdater
    from services.metadata.updater import MetadataUpdater
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
        metadata_updater: MetadataUpdater,
        recently_added_cache: MoviesCache,
        missing_artworks_cache: MoviesCache,
        sleep_interval: float = 1.0,
    ) -> None:
        self.plex_manager = plex_manager
        self.artworks_updater = artworks_updater
        self.sleep_interval = sleep_interval
        self.metadata_updater = metadata_updater
        self.recent_cache = recently_added_cache
        self.missing_cache = missing_artworks_cache

    def run(self) -> None:
        self.recent_cache.load()
        self.missing_cache.load()

        recently_added_movies = self.plex_manager.get_recently_added_movies()
        if not recently_added_movies:
            logger.info("No recently added movies found.")
            return

        for movie in recently_added_movies:
            if movie in self.recent_cache:
                continue

            self.process_movie(movie)

            time.sleep(self.sleep_interval)

        # Trim cache so only the most recent movies remain relevant
        last_movie = recently_added_movies[-1]
        self.recent_cache.clear(last_movie)

        self.recent_cache.save()
        self.missing_cache.save()

    def process_movie(self, movie: Movie) -> None:
        tmdb_id = self.plex_manager.get_tmdb_id(movie["plex_movie_id"])
        if not tmdb_id:
            logger.warning(
                f"Movie {movie['title']} is not matched in TMDB. Skipping it for now."
            )
            return

        movie["tmdb_id"] = tmdb_id
        status, artworks = self.artworks_updater.update(movie, None)

        if status == "upload_failed":
            logger.warning(f"✗ Upload failed for {movie['title']}")
            return

        self.metadata_updater.update_release_date(movie)
        self.recent_cache.add(movie)

        if status == "success":
            logger.info(f"✓ Complete artworks found for {movie['title']}")
            return

        movie_with_artworks = movie.copy()
        movie_with_artworks["artworks"] = artworks
        self.missing_cache.add(movie_with_artworks)

        if status == "empty_artworks":
            logger.info(f"⚠ No artworks found for {movie['title']}")
        elif status == "imperfect_artworks":
            logger.info(f"⚠ Incomplete artworks found for {movie['title']}")
